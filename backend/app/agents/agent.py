"""Transportation Infrastructure Analysis Agent."""
import json
import logging
import re
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from openai import OpenAIError
from app.agents.navigator_client import NavigatorClient
from app.agents.prompts import build_system_message, build_user_message, build_tool_result_message
from app.agents.tool_registry import AGENT_TOOLS
from app.agents.tools import execute_tool
from app.schemas import ChatRequest, ChatResponse, TrafficResult, IntersectionCandidate, MapFeature
from app.services.validation_service import validate_traffic_result, create_no_data_result
from app.gis.intersection import find_nearby_intersections, resolve_intersection, get_intersection_details
from app.gis.traffic import (
    find_traffic_sites_near_intersection,
    get_hourly_traffic_volume,
    get_aadt_near_intersection,
    get_signal_info_near_intersection,
    get_available_data_near_intersection,
)

logger = logging.getLogger(__name__)

MAX_TOOL_CALLS = 5

class TransportationAgent:
    def __init__(self):
        self.navigator = NavigatorClient()

    def _fallback_process(
        self,
        request: ChatRequest,
        session: Optional[Session],
    ) -> ChatResponse:
        """Deterministic fallback when NaviGator AI API key is not configured or offline."""
        msg_lower = request.message.lower()
        
        # 1. Location / intersection search request
        if request.location and not request.selected_intersection_id:
            candidates = find_nearby_intersections(
                session, request.location.latitude, request.location.longitude, 250.0
            )
            resolution = resolve_intersection(candidates)
            if resolution["status"] == "not_found":
                return ChatResponse(
                    status="no_data",
                    message="No authoritative FDOT intersections were found within 500 meters of the selected location.",
                    candidates=[],
                    conversation_id=request.conversation_id,
                )
            elif resolution["status"] == "needs_clarification":
                return ChatResponse(
                    status="needs_clarification",
                    message=f"I found {len(candidates)} intersections near your selected location. Please select one to analyze:",
                    candidates=candidates,
                    conversation_id=request.conversation_id,
                )
            else:
                inter = resolution["intersection"]
                return ChatResponse(
                    status="answer",
                    message=f"Location identified: {inter.name} ({inter.distance_m}m away). What transportation information would you like to know?",
                    candidates=[inter],
                    conversation_id=request.conversation_id,
                )
                
        # 2. Selected intersection query
        if request.selected_intersection_id:
            inter_id = int(request.selected_intersection_id)
            details = get_intersection_details(session, inter_id)
            inter_name = details.get("roadway", "Selected Intersection") if details else f"Intersection #{inter_id}"
            if details and details.get("intersecting_roadway"):
                inter_name = f"{details['roadway']} & {details['intersecting_roadway']}"
                
            # Question about Traffic Signals
            if "signal" in msg_lower or "traffic light" in msg_lower:
                signals = get_signal_info_near_intersection(session, inter_id, 250)
                if signals:
                    closest = signals[0]
                    res = validate_traffic_result(
                        value=1.0,
                        metric_requested="traffic_signal",
                        metric_available="signal_status",
                        source_agency="FDOT",
                        source_dataset="Traffic Signal Locations TDA",
                        source_url="https://services1.arcgis.com/O1JpcwDW8sjYuddV/ArcGIS/rest/services/Traffic_Signal_Locations_TDA/FeatureServer/0",
                        unit="signal",
                        record_id=str(closest.get("id")),
                        spatial_relation=f"{closest.get('distance_m', 0):.1f}m from intersection",
                        distance_m=closest.get("distance_m")
                    )
                    return ChatResponse(
                        status="answer",
                        message=f"Yes, this intersection is signalized. FDOT Traffic Signal record ({closest.get('signal_type', 'Traffic Control Signal')}) is located {closest.get('distance_m', 0):.1f}m away on {closest.get('roadway', 'the corridor')}.",
                        result=res,
                        conversation_id=request.conversation_id
                    )
                else:
                    res = create_no_data_result("No authoritative FDOT traffic signal record was found within 250m of this intersection.")
                    return ChatResponse(
                        status="answer",
                        message=f"No authoritative FDOT traffic signal record was found within 250m of {inter_name}. It may be unsignalized or locally operated without a state record.",
                        result=res,
                        conversation_id=request.conversation_id
                    )

            # Real-time traffic / traffic jam / "is there traffic" inquiries
            if any(w in msg_lower for w in ["traffic jam", "congestion", "jam", "right now", "live traffic", "current traffic", "real time", "real-time", "accident", "crash", "is there traffic", "is it busy", "is traffic bad"]):
                segments = get_aadt_near_intersection(session, inter_id, 500)
                signals = get_signal_info_near_intersection(session, inter_id, 250)
                sig_count = len(signals)
                
                if segments:
                    best = segments[0]
                    aadt = best.get("aadt", 0)
                    road = best.get("roadway", "the corridor")
                    year = f" ({best.get('aadt_year')})" if best.get("aadt_year") else ""
                    
                    if aadt >= 20000:
                        level = "high-volume, heavily traveled arterial corridor"
                        typical = "substantial traffic and noticeable delays, especially during morning (7:30–9:00 AM) and evening (4:30–6:30 PM) peak commute hours"
                    elif aadt >= 8000:
                        level = "moderate-volume roadway"
                        typical = "steady traffic flow with occasional slowdowns during peak hours"
                    else:
                        level = "low-to-moderate volume collector street"
                        typical = "generally light and free-flowing traffic"
                        
                    sig_desc = f"{sig_count} traffic signal control(s) present" if sig_count > 0 else "no state-recorded traffic signals"
                    
                    msg = (
                        f"No, the system does not monitor live, real-time traffic conditions or active traffic jams at {inter_name}.\n\n"
                        f"However, based on authoritative FDOT records, this roadway carries an Annual Average Daily Traffic (AADT) of **{aadt:,} vehicles/day**{year} on {road}, with {sig_desc}.\n\n"
                        f"**Estimated Assumption**: Because this is a {level}, you can reasonably assume it typically experiences {typical}. "
                        f"*(Note: This is an educated assumption derived from annualized AADT data, not a live real-time observation.)*"
                    )
                    
                    res = validate_traffic_result(
                        value=float(aadt),
                        metric_requested="traffic_conditions",
                        metric_available="AADT",
                        source_agency=best.get("source_agency", "FDOT"),
                        source_dataset=best.get("dataset", "Annual Average Daily Traffic"),
                        source_url="https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/0",
                        unit="vehicles/day",
                        record_id=str(best.get("id")),
                        spatial_relation="roadway segment adjacent to intersection",
                        distance_m=best.get("distance_m", 50.0)
                    )
                    return ChatResponse(
                        status="answer",
                        message=msg,
                        result=res,
                        conversation_id=request.conversation_id
                    )
                else:
                    return ChatResponse(
                        status="answer",
                        message=(
                            f"No, the system does not monitor live, real-time traffic conditions or active traffic jams at {inter_name}. "
                            f"Furthermore, no authoritative AADT or count records were found within 500m to assess typical traffic levels."
                        ),
                        result=create_no_data_result("Real-time live traffic monitoring is out of scope, and no nearby historical volume was found."),
                        conversation_id=request.conversation_id
                    )

            # Question about Hourly Traffic Volume (Target Metric)
            if any(w in msg_lower for w in ["hourly", "5 pm", "5 to 6", "hour", "yesterday", "am", "morning", "evening", "interval"]):
                sites = find_traffic_sites_near_intersection(session, inter_id, 500)
                segments = get_aadt_near_intersection(session, inter_id, 500)
                
                # Rule 5 & 22: Distinguish hourly traffic volume from AADT
                if segments:
                    aadt_val = segments[0]["aadt"]
                    aadt_year = segments[0].get("aadt_year", "recent")
                    return ChatResponse(
                        status="no_data",
                        message=(
                            f"No authoritative hourly traffic-volume observation was found for {inter_name}. "
                            f"Note: An AADT value of {aadt_val:,} vehicles/day ({aadt_year}) is available on the nearby roadway segment, "
                            f"but AADT is an annualized daily average and is not the requested hourly volume."
                        ),
                        result=create_no_data_result("No authoritative hourly volume observation recorded at this intersection."),
                        conversation_id=request.conversation_id
                    )
                else:
                    return ChatResponse(
                        status="no_data",
                        message=f"No authoritative hourly traffic-volume observation was found for {inter_name}.",
                        result=create_no_data_result("No authoritative hourly traffic volume data found."),
                        conversation_id=request.conversation_id
                    )

            # Question about AADT, Daily Volume, or General Vehicle Counts ("how many vehicles")
            if any(w in msg_lower for w in ["aadt", "daily", "average", "how many", "count", "vehicles", "cars", "volume", "traffic flow", "how much"]):
                segments = get_aadt_near_intersection(session, inter_id, 500)
                if segments:
                    best = segments[0]
                    res = validate_traffic_result(
                        value=float(best["aadt"]),
                        metric_requested="annual_average_daily_traffic",
                        metric_available="AADT",
                        source_agency=best.get("source_agency", "FDOT"),
                        source_dataset=best.get("dataset", "Annual Average Daily Traffic"),
                        source_url="https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/0",
                        unit="vehicles/day",
                        record_id=str(best.get("id")),
                        spatial_relation="roadway segment adjacent to intersection",
                        distance_m=best.get("distance_m", 50.0)
                    )
                    year_info = f" (Year {best['aadt_year']})" if best.get("aadt_year") else ""
                    return ChatResponse(
                        status="answer",
                        message=f"According to FDOT records, the Annual Average Daily Traffic (AADT) near {inter_name} is {best['aadt']:,} vehicles/day{year_info} on {best.get('roadway', 'the roadway segment')}.",
                        result=res,
                        conversation_id=request.conversation_id
                    )
                else:
                    res = create_no_data_result("No authoritative AADT record found for the adjacent roadway segment.")
                    return ChatResponse(
                        status="no_data",
                        message=f"No authoritative daily volume (AADT) record was found within 500m of {inter_name}.",
                        result=res,
                        conversation_id=request.conversation_id
                    )

            # General information request
            avail = get_available_data_near_intersection(session, inter_id, 500)
            summary_lines = []
            if avail.get("traffic_signals_count", 0) > 0:
                summary_lines.append(f"• Traffic Signal: Yes ({avail['traffic_signals_count']} signal record nearby)")
            else:
                summary_lines.append("• Traffic Signal: None recorded in state inventory")
                
            if avail.get("aadt_segments_count", 0) > 0:
                seg = avail["closest_aadt_segment"]
                summary_lines.append(f"• AADT: {seg['aadt']:,} vehicles/day on {seg['roadway']}")
            else:
                summary_lines.append("• AADT: None recorded nearby")
                
            if avail.get("traffic_sites_count", 0) > 0:
                summary_lines.append(f"• Traffic Monitoring Sites: {avail['traffic_sites_count']} monitoring sites nearby")
                
            return ChatResponse(
                status="answer",
                message=f"Transportation data available for {inter_name}:\n" + "\n".join(summary_lines),
                conversation_id=request.conversation_id
            )

        return ChatResponse(
            status="answer",
            message="Please click a point on the map or enter an address to select an intersection in Gainesville.",
            conversation_id=request.conversation_id
        )

    def process_query(
        self,
        request: ChatRequest,
        session: Optional[Session],
    ) -> ChatResponse:
        """Process a user query through the agent loop with tool execution."""
        
        # Check if NaviGator API is configured
        if not self.navigator.is_configured():
            logger.info("NaviGator API key not configured; using deterministic transportation engine.")
            return self._fallback_process(request, session)
        
        # Build initial messages for LLM
        messages = [build_system_message()]
        
        # Add location context if available
        location_context = []
        if getattr(request, "location", None):
            location_context.append(f"Coordinates: lat={request.location.latitude}, lon={request.location.longitude} (source={request.location.source})")
        if getattr(request, "selected_intersection_id", None):
            location_context.append(f"Selected intersection ID: {request.selected_intersection_id}")
            
        context_str = ", ".join(location_context) if location_context else None
        messages.append(build_user_message(request.message, context_str))
        
        last_candidates: Optional[List[IntersectionCandidate]] = None
        last_result: Optional[TrafficResult] = None
        
        # Agent loop with bounded tool calls
        for iteration in range(MAX_TOOL_CALLS):
            try:
                response = self.navigator.chat_completion(
                    messages=messages,
                    tools=AGENT_TOOLS,
                )
            except OpenAIError as e:
                logger.error(f"NaviGator API error during agent loop: {e}. Falling back to deterministic engine.")
                return self._fallback_process(request, session)
            except Exception as e:
                logger.error(f"Unexpected error during agent loop: {e}. Falling back to deterministic engine.")
                return self._fallback_process(request, session)
            
            choice = response.choices[0]
            message = choice.message
            
            # If no tool calls, return final response
            if not message.tool_calls:
                # Classify status based on message content
                content = message.content or "No response provided."
                status = "answer"
                if (last_result and last_result.result_type == "UNAVAILABLE") or "no authoritative" in content.lower() or "not found" in content.lower():
                    status = "no_data"
                    if last_result is None:
                        last_result = create_no_data_result("No authoritative observation exists for the requested query.")
                elif "which one" in content.lower() or "multiple intersections" in content.lower():
                    status = "needs_clarification"
                    
                return ChatResponse(
                    status=status,
                    message=content,
                    result=last_result,
                    candidates=last_candidates,
                    conversation_id=request.conversation_id,
                )
            
            # Append assistant message with tool calls
            messages.append(message.model_dump(exclude_unset=True))
            
            # Execute each tool call
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                
                logger.info(f"Agent executing tool: {tool_name} with args: {arguments}")
                raw_result = execute_tool(tool_name, arguments, session)
                
                # Check if tool returned candidate intersections
                if tool_name == "find_nearby_intersections":
                    try:
                        parsed_list = json.loads(raw_result)
                        if isinstance(parsed_list, list) and parsed_list:
                            last_candidates = [IntersectionCandidate(**item) for item in parsed_list if isinstance(item, dict)]
                    except Exception:
                        pass
                elif tool_name == "get_aadt_near_intersection":
                    try:
                        parsed_data = json.loads(raw_result)
                        if isinstance(parsed_data, list) and parsed_data:
                            best = parsed_data[0]
                            last_result = validate_traffic_result(
                                value=float(best["aadt"]),
                                metric_requested="annual_average_daily_traffic",
                                metric_available="AADT",
                                source_agency=best.get("source_agency", "FDOT"),
                                source_dataset=best.get("dataset", "Annual Average Daily Traffic"),
                                source_url="https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/0",
                                unit="vehicles/day",
                                record_id=str(best.get("id")),
                                spatial_relation="roadway segment adjacent to intersection",
                                distance_m=best.get("distance_m", 50.0)
                            )
                    except Exception:
                        pass
                elif tool_name == "get_hourly_traffic_volume":
                    try:
                        parsed_data = json.loads(raw_result)
                        if isinstance(parsed_data, dict) and parsed_data.get("result_type") == "UNAVAILABLE":
                            last_result = TrafficResult(
                                result_type="UNAVAILABLE",
                                message=parsed_data.get("message", "No hourly volume observation exists.")
                            )
                    except Exception:
                        pass
                        
                messages.append(build_tool_result_message(tool_call.id, raw_result))
        
        # Exceeded max iterations
        return ChatResponse(
            status="error",
            message="The request required too many steps. Please narrow your question or select an intersection directly on the map.",
            conversation_id=request.conversation_id,
        )
