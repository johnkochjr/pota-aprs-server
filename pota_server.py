#!/usr/bin/env python3
import aprslib
import requests
import time
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/pota_aprs.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ===== CONFIGURATION - EDIT THESE =====
CALLSIGN = "AI5KP"      # Your callsign without SSID
SSID = "10"                 # SSID for this server (e.g., 10 = YOURCALL-10)
PASSCODE = "22496"  # Get from https://apps.magicbug.co.uk/passcode/
# ======================================

def get_pota_spots(limit=5):
    """Fetch recent POTA spots from API"""
    try:
        response = requests.get("https://api.pota.app/spot/activator", timeout=10)
        response.raise_for_status()
        spots = response.json()
        logger.info(f"Fetched {len(spots)} POTA spots from API")
        return spots[:limit]
    except requests.exceptions.Timeout:
        logger.error("Timeout fetching POTA spots")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching POTA spots: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching spots: {e}")
        return []

def format_pota_messages(spots):
    """Format POTA spots for APRS (67 char limit per message)"""
    if not spots:
        return ["No POTA spots available"]
    
    messages = []
    for idx, spot in enumerate(spots[:5], 1):
        activator = spot.get('activator', 'N/A')
        freq = spot.get('frequency', 'N/A')
        reference = spot.get('reference', 'N/A')
        mode = spot.get('mode', 'N/A')
        
        # Format: "1:W1ABC 14.260 K-1234 SSB"
        msg = f"{idx}:{activator} {freq} {reference} {mode}"
        
        # Ensure under 67 characters
        if len(msg) > 67:
            msg = msg[:64] + "..."
        messages.append(msg)
    
    return messages

def callback(packet):
    """Process incoming APRS messages"""
    try:
        # Check if it's a message addressed to us
        if (packet.get('format') == 'message' and 
            packet.get('addresse') == f"{CALLSIGN}-{SSID}"):
            
            from_call = packet['from']
            message_text = packet.get('message_text', '').strip().lower()
            msg_id = packet.get('msgNo', '')
            
            logger.info(f"📨 Message from {from_call}: '{message_text}' (msgNo: {msg_id})")
            
            # Check for POTA query keywords
            if any(keyword in message_text for keyword in ['pota', 'spot', 'spots', 'help']):
                logger.info("Processing POTA request...")
                
                # Fetch spots
                spots = get_pota_spots(limit=5)
                messages = format_pota_messages(spots)
                
                # Send acknowledgement first
                if msg_id:
                    try:
                        ack_frame = f"{CALLSIGN}-{SSID}>APRS,TCPIP*::{from_call:<9}:ack{msg_id}"
                        AIS.sendall(ack_frame)
                        logger.info(f"✓ Sent ACK to {from_call}")
                        time.sleep(1)
                    except Exception as e:
                        logger.error(f"Failed to send ACK: {e}")
                
                # Send spot responses
                for idx, msg in enumerate(messages):
                    try:
                        frame = f"{CALLSIGN}-{SSID}>APRS,TCPIP*::{from_call:<9}:{msg}"
                        AIS.sendall(frame)
                        logger.info(f"📤 Sent ({idx+1}/{len(messages)}): {msg}")
                        time.sleep(2)  # Rate limiting
                    except Exception as e:
                        logger.error(f"Failed to send message: {e}")
                        
    except Exception as e:
        logger.error(f"Error processing packet: {e}", exc_info=True)

def main():
    """Main server loop"""
    global AIS
    
    logger.info("=" * 60)
    logger.info("🚀 POTA APRS Server Starting...")
    logger.info(f"📻 Callsign: {CALLSIGN}-{SSID}")
    logger.info("=" * 60)
    
    # Validate configuration
    if CALLSIGN == "YOUR-CALL" or PASSCODE == "YOUR-PASSCODE":
        logger.error("❌ Please configure your CALLSIGN and PASSCODE in the script!")
        sys.exit(1)
    
    try:
        # Connect to APRS-IS
        logger.info("🔌 Connecting to APRS-IS...")
        AIS = aprslib.IS(f"{CALLSIGN}-{SSID}", passwd=PASSCODE, port=14580)
        AIS.connect()
        logger.info("✓ Connected to APRS-IS")
        
        # Send status beacon
        beacon = f"{CALLSIGN}-{SSID}>APRS,TCPIP*:>POTA Spot Server v1.0 - Send 'POTA' for spots"
        AIS.sendall(beacon)
        logger.info("✓ Status beacon sent")
        logger.info("👂 Listening for messages...")
        
        # Start listening (immortal=True will auto-reconnect)
        AIS.consumer(callback, blocking=True, immortal=True, raw=False)
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  Shutdown requested...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
    finally:
        try:
            AIS.close()
            logger.info("👋 Disconnected from APRS-IS")
        except:
            pass

if __name__ == "__main__":
    main()
