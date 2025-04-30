from srlinux.syntax import Syntax
from srlinux.location import build_path
from srlinux.mgmt.cli import KeyCompleter
import datetime

class IpBgpReport:
    """Handles the 'show ip bgp summary' command functionality."""
    
    # Class level constants
    PATH_TEMPLATES = {
        'bgp_instance': '/network-instance[name={network_instance}]/protocols/bgp',
    }

    BGP_STATE_MAP = {
        'idle': 'Idle',
        'connect': 'Connect',
        'active': 'Active',
        'opensent': 'OpenSent',
        'openconfirm': 'OpenConfirm',
        'established': 'Estab'
    }

    def show_bgp_summary(self, state, output, network_instance='default'):
        """Main function to display BGP summary"""
        # Get BGP instance data
        try:
            bgp_data = self._get_bgp_data(state, network_instance)
            # Silently exit if no data found (don't print error messages)
            if not bgp_data:
                return
                
            if not self._has_bgp_config(bgp_data):
                return
                
            # Print header and neighbor data
            self._print_bgp_header(bgp_data, network_instance)
            neighbors = self._get_neighbor_data(bgp_data)
            
            if neighbors:
                self._print_neighbor_table(neighbors)
            else:
                # No neighbors - exit silently
                pass
                
        except Exception as e:
            # Silent error handling - don't print errors
            pass

    def _get_bgp_data(self, state, network_instance):
        """Get BGP instance data"""
        try:
            path = build_path(self.PATH_TEMPLATES['bgp_instance'].format(
                network_instance=network_instance
            ))
            return state.server_data_store.get_data(path, recursive=True)
        except Exception:
            # Silently handle error
            return None

    def _has_bgp_config(self, bgp_data):
        """Check if BGP is configured"""
        if not bgp_data:
            return False
            
        try:
            network_instance = bgp_data.network_instance.get()
            if not network_instance:
                return False
                
            protocols = network_instance.protocols.get()
            if not protocols:
                return False
                
            return bool(protocols.bgp.get())
        except (AttributeError, Exception):
            return False

    def _print_bgp_header(self, bgp_data, network_instance):
        """Print BGP header information"""
        router_id = "0.0.0.0"
        local_as = "N/A"
        
        try:
            bgp = bgp_data.network_instance.get().protocols.get().bgp.get()
            if hasattr(bgp, 'router_id') and bgp.router_id:
                router_id = bgp.router_id
                
            if hasattr(bgp, 'autonomous_system') and bgp.autonomous_system:
                local_as = bgp.autonomous_system
        except (AttributeError, Exception):
            pass
            
        print(f"BGP summary information for VRF {network_instance}")
        print(f"Router identifier {router_id}, local AS number {local_as}")
        print("Neighbor Status Codes: m – Under maintenance")
        
        # Print column headers
        print("  Neighbor        V    AS     MsgRcvd   MsgSent   InQ    OutQ   Up/Down   State     PfxRcd    PfxAcc")

    def _get_neighbor_data(self, bgp_data):
        """Get BGP neighbor data"""
        neighbors = []
        
        try:
            bgp = bgp_data.network_instance.get().protocols.get().bgp.get()
            if not hasattr(bgp, 'neighbor'):
                return neighbors
                
            for neighbor in bgp.neighbor.items():
                if not neighbor:
                    continue
                # check for EVPN neighbors
                if hasattr(neighbor, 'afi_safi'):
                    for afi_safi in neighbor.afi_safi.items():
                        if not afi_safi:
                            continue   
                        if afi_safi.afi_safi_name == 'ipv4-unicast' and afi_safi.admin_state == 'enable':
                            # Extract neighbor data with safe defaults
                            peer_address = neighbor.peer_address
                            peer_as = "?" 
                            if hasattr(neighbor, 'peer_as'):
                                peer_as = str(neighbor.peer_as)
                            # Get session state - be cautious about case sensitivity
                            session_state = "Idle"
                            state_lower = None
                            if hasattr(neighbor, 'session_state'):
                                state_lower = neighbor.session_state.lower() if neighbor.session_state else None
                                # Map to display format with proper capitalization
                                session_state = self.BGP_STATE_MAP.get(state_lower, "Idle")
                
                            # Get message statistics
                            messages_received = 0
                            messages_sent = 0
                
                            if hasattr(neighbor, 'received_messages'):
                                rm = neighbor.received_messages.get()
                                if rm and hasattr(rm, 'total_messages'):
                                    messages_received = rm.total_messages
                                    received_queue = rm.queue_depth
                        
                            if hasattr(neighbor, 'sent_messages'):
                                sm = neighbor.sent_messages.get()
                                if sm and hasattr(sm, 'total_messages'):
                                    messages_sent = sm.total_messages
                                    sent_queue = sm.queue_depth
                            # Get prefix information
                            prefixes_received = 0
                            prefixes_accepted = 0                                       
                            if hasattr(afi_safi, 'received_routes'):
                                prefixes_received = afi_safi.received_routes
                            if hasattr(afi_safi, 'active_routes'):
                                prefixes_accepted = afi_safi.active_routes
                
                            # Format uptime
                            uptime = self._format_uptime(neighbor)
                            neighbor_info = {
                                'peer_address': peer_address,
                                'address_family': "4",
                                'peer_as': peer_as,
                                'msg_rcvd': messages_received,
                                'msg_sent': messages_sent,
                                'state': session_state,
                                'state_lower': state_lower,
                                'pfx_received': prefixes_received,
                                'pfx_accepted': prefixes_accepted,
                                'up_time': uptime,
                                'rx_queue': received_queue,
                                'tx_queue': sent_queue
                            }
                            neighbors.append(neighbor_info)
                        if afi_safi.afi_safi_name == 'ipv6-unicast' and afi_safi.admin_state == 'enable':
                            # Extract neighbor data with safe defaults
                            peer_address = neighbor.peer_address
                            peer_as = "?" 
                            if hasattr(neighbor, 'peer_as'):
                                peer_as = str(neighbor.peer_as)
                            # Get session state - be cautious about case sensitivity
                            session_state = "Idle"
                            state_lower = None
                            if hasattr(neighbor, 'session_state'):
                                state_lower = neighbor.session_state.lower() if neighbor.session_state else None
                                # Map to display format with proper capitalization
                                session_state = self.BGP_STATE_MAP.get(state_lower, "Idle")
                
                            # Get message statistics
                            messages_received = 0
                            messages_sent = 0
                
                            if hasattr(neighbor, 'received_messages'):
                                rm = neighbor.received_messages.get()
                                if rm and hasattr(rm, 'total_messages'):
                                    messages_received = rm.total_messages
                                    received_queue = rm.queue_depth
                        
                            if hasattr(neighbor, 'sent_messages'):
                                sm = neighbor.sent_messages.get()
                                if sm and hasattr(sm, 'total_messages'):
                                    messages_sent = sm.total_messages
                                    sent_queue = sm.queue_depth
                            # Get prefix information
                            prefixes_received = 0
                            prefixes_accepted = 0                                       
                            if hasattr(afi_safi, 'received_routes'):
                                prefixes_received = afi_safi.received_routes
                            if hasattr(afi_safi, 'active_routes'):
                                prefixes_accepted = afi_safi.active_routes
                
                            # Format uptime
                            uptime = self._format_uptime(neighbor)
                            neighbor_info = {
                                'peer_address': peer_address,
                                'address_family': "6",
                                'peer_as': peer_as,
                                'msg_rcvd': messages_received,
                                'msg_sent': messages_sent,
                                'state': session_state,
                                'state_lower': state_lower,
                                'pfx_received': prefixes_received,
                                'pfx_accepted': prefixes_accepted,
                                'up_time': uptime,
                                'rx_queue': received_queue,
                                'tx_queue': sent_queue
                            }
                            neighbors.append(neighbor_info)
                        if afi_safi.afi_safi_name == 'evpn' and afi_safi.admin_state == 'enable':
                            # Extract neighbor data with safe defaults
                            peer_address = neighbor.peer_address
                            peer_as = "?" 
                            if hasattr(neighbor, 'peer_as'):
                                peer_as = str(neighbor.peer_as)
                            # Get session state - be cautious about case sensitivity
                            session_state = "Idle"
                            state_lower = None
                            if hasattr(neighbor, 'session_state'):
                                state_lower = neighbor.session_state.lower() if neighbor.session_state else None
                                # Map to display format with proper capitalization
                                session_state = self.BGP_STATE_MAP.get(state_lower, "Idle")
                
                            # Get message statistics
                            messages_received = 0
                            messages_sent = 0
                
                            if hasattr(neighbor, 'received_messages'):
                                rm = neighbor.received_messages.get()
                                if rm and hasattr(rm, 'total_messages'):
                                    messages_received = rm.total_messages
                                    received_queue = rm.queue_depth
                        
                            if hasattr(neighbor, 'sent_messages'):
                                sm = neighbor.sent_messages.get()
                                if sm and hasattr(sm, 'total_messages'):
                                    messages_sent = sm.total_messages
                                    sent_queue = sm.queue_depth
                            # Get prefix information
                            prefixes_received = 0
                            prefixes_accepted = 0                                       
                            if hasattr(afi_safi, 'received_routes'):
                                prefixes_received = afi_safi.received_routes
                            if hasattr(afi_safi, 'active_routes'):
                                prefixes_accepted = afi_safi.active_routes
                
                            # Format uptime
                            uptime = self._format_uptime(neighbor)
                            neighbor_info = {
                                'peer_address': peer_address,
                                'address_family': "E",
                                'peer_as': peer_as,
                                'msg_rcvd': messages_received,
                                'msg_sent': messages_sent,
                                'state': session_state,
                                'state_lower': state_lower,
                                'pfx_received': prefixes_received,
                                'pfx_accepted': prefixes_accepted,
                                'up_time': uptime,
                                'rx_queue': received_queue,
                                'tx_queue': sent_queue
                            }
                            neighbors.append(neighbor_info)
               
        except Exception:
            # Silent error handling
            pass
            
        return neighbors

    def _create_route_entry(self, route_network, status):
        """Create basic route entry with standard fields"""
        return {
            'network_info': route_network,
            'status_info': status,
            'nexthop_info': '',
            'metric_info': '',
            'locpref_info': '',
            'weight_info': '',
            'path_info': ''
        }

    def _populate_route_attrs(self, state, route_entry, netinst_name, attr_id, route_type='*'):
        if not attr_id in self._attrSets_dict:
            path_attr = build_path('/network-instance[name={vrf}]/bgp-rib/attr-sets/attr-set[index={atr}]',
                              vrf=netinst_name, atr=str(attr_id))
            attrSets = state.server_data_store.get_data(path_attr, recursive=True, include_container_children=True)
            self._attrSets_dict[attr_id] = attrSets
        else:
            attrSets = self._attrSets_dict[attr_id]
        for attr in attrSets.get_descendants('/network-instance/bgp-rib/attr-sets/attr-set'):
            route_entry['nexthop_info'] = attr.next_hop
            route_entry['locpref_info'] = attr.local_pref
            as_path = attr.as_path.get().segment.get().member
            if attr.origin == 'igp':
                route_entry['path_info'] = ' '.join(map(str,as_path)) + ' i'
            elif attr.origin == 'egp':
                route_entry['path_info'] = ' '.join(map(str,as_path)) + ' e'
            elif attr.origin == 'incomplete':
                route_entry['path_info'] = '?'
            if hasattr(attr, 'med') and attr.med:
                route_entry['metric_info'] = attr.med
            else:
                route_entry['metric_info'] = '-'
            route_entry['weight_info'] = '0'

    def _set_status_code(self, route):
        status = ""
        if route.used_route:
            status = "u"
            #self._used_routes += 1
        if route.stale_route:
            status += "x"
            #self._statle_routes += 1
        if route.valid_route:
            status += "*"
            #self._valid_routes += 1
        if route.best_route:
            status += ">"
        return status or '-'

    def _print_neighbor_table(self, neighbors):
        """Print formatted neighbor table"""
        for neighbor in sorted(neighbors, key=lambda x: str(x.get('peer_address', ''))):
            # Show the correct format based on BGP state
            # For established neighbors, show the prefix count
            # For non-established, show the state
            if neighbor.get('state_lower') == 'established':
                state_display = str(neighbor.get('pfx_received', 0))
            else:
                state_display = neighbor.get('state', 'Idle')
            
            print(f"  {neighbor['peer_address']:<15} {neighbor['address_family']:<1}    {neighbor['peer_as']:<6} "
                  f"{neighbor['msg_rcvd']:<9} {neighbor['msg_sent']:<9} "
                  f"{neighbor['rx_queue']:<6} {neighbor['tx_queue']:<6} "
                  f"{neighbor['up_time']:<9} {neighbor['state']:<9} " 
                  f"{neighbor['pfx_received']:<9} {neighbor['pfx_accepted']:<9}")

    def _format_uptime(self, neighbor):
        """Format uptime for display with safer parsing"""
        # Default for non-established sessions
        if not hasattr(neighbor, 'session_state') or neighbor.session_state != 'established':
            return "never"
        
        # Check if last_established exists and has a value
        if not hasattr(neighbor, 'last_established') or not neighbor.last_established:
            return "never"
            
        try:
            # Safer parsing that handles potential format variations
            timestamp_str = neighbor.last_established
            if '(' in timestamp_str:
                timestamp_str = timestamp_str.split('(')[0].strip()
                
            # Handle ISO format timestamps with timezone information
            if 'Z' in timestamp_str:
                timestamp_str = timestamp_str.replace('Z', '+00:00')
                
            last_established_time = datetime.datetime.fromisoformat(timestamp_str)
            current_time = datetime.datetime.now(datetime.timezone.utc)
            
            # Handle potential timezone differences
            if last_established_time.tzinfo is None:
                last_established_time = last_established_time.replace(tzinfo=datetime.timezone.utc)
                
            uptime = current_time - last_established_time
            
            # Format the uptime string
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            
            if days > 0:
                return f"{days}d{hours}h"
            elif hours > 0:
                return f"{hours}h{minutes}m"
            else:
                return f"{minutes}m"
                
        except Exception:
            # Fall back to "never" if there's any parsing error
            return "never"

    def _print_rt_table(self, rt_entries):
        """Print formatted route type table"""
        for rt_entry in rt_entries:    
            print(f" {rt_entry['status_info']:<7} {rt_entry['network_info']:<50}\n "
                  f"                            {rt_entry['nexthop_info']:<16} {rt_entry['metric_info']:<7} "
                  f"{rt_entry['locpref_info']:<7} {rt_entry['weight_info']:<6} "
                  f"{rt_entry['path_info']:<20} ")
