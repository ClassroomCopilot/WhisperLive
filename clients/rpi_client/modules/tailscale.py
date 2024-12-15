import subprocess
import json

def get_tailscale_ips():
    result = subprocess.run(['tailscale', 'status', '--json'], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception("Failed to get Tailscale status")
    
    # Parse the JSON response
    status = json.loads(result.stdout)
    
    # Access the 'Self' key to get the Tailscale IPs
    self_info = status.get('Self', {})
    
    if not self_info:
        print("No self information found in Tailscale status")
        return []
    
    ips = self_info.get('TailscaleIPs', [])
    
    if not ips:
        print("No Tailscale IPs found")
    
    return ips