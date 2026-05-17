import time
from pygame import mixer
from nyct_gtfs import NYCTFeed

# ==========================================
# 1. AUDIO CONFIGURATION
# ==========================================
mixer.init()
try:
    arrival_sound = mixer.Sound("arrival.mp3")
    departure_sound = mixer.Sound("departure.mp3")
    print("Audio files loaded successfully.")
except Exception as e:
    print(f"Error loading audio files: {e}")
    print("Please make sure 'arrival.mp3' and 'departure.mp3' are in this folder.")
    exit()

# ==========================================
# 2. MTA CONFIGURATION
# ==========================================
# "1" loads the feed containing the 1, 2, 3, 4, 5, 6 lines
FEED_LINE = "1"
# '117' is 137 St-City College. 'S' stands for Southbound (Downtown).
TARGET_STOP = "117S"  

# State tracking variable to detect when a train arrives or leaves
was_train_in_station = False

print("Starting Subway Audio Monitor System for 137th St (Downtown 1)...")
print("Press Ctrl+C to stop.")
print("-" * 50)

# ==========================================
# 3. MAIN MONITORING LOOP
# ==========================================
try:
    while True:
        try:
            # Fetch the live, real-time feed from the MTA
            feed = NYCTFeed(FEED_LINE)
            
            is_train_in_station_now = False
            
            # Look through all active trips currently on the line
            for train in feed.trips:
                # If the train has no upcoming stop data, skip it
                if not train.stop_time_updates:
                    continue
                
                # The first update in the list represents the train's CURRENT active stop
                current_update = train.stop_time_updates[0]
                
                # Extract the stop ID and the train's real-time status at that stop
                current_stop = current_update.stop_id                         # e.g., '117S'
                status = getattr(current_update, 'current_status', None)      # e.g., 'STOPPED_AT'
                
                # Check if it matches our downtown 137th St target and is physically stopped
                if current_stop == TARGET_STOP and status == "STOPPED_AT":
                    is_train_in_station_now = True
                    break # Found it! No need to check other trains during this specific loop cycle
            
            # --- State Transition Logic ---
            
            # Case A: Train just arrived (It wasn't there 15 seconds ago, but it is now)
            if is_train_in_station_now and not was_train_in_station:
                print(f"[{time.strftime('%X')}] [ARRIVED] Downtown 1 train has entered 137th St! Playing sound...")
                arrival_sound.play()
                
            # Case B: Train just left (It was there 15 seconds ago, but it isn't now)
            elif not is_train_in_station_now and was_train_in_station:
                print(f"[{time.strftime('%X')}] [DEPARTED] Train has left 137th St. Playing sound...")
                departure_sound.play()
                
            else:
                # Idle reporting just to let you know the script is alive
                if is_train_in_station_now:
                    print(f"[{time.strftime('%X')}] Train is still stopped at the platform...")
                else:
                    print(f"[{time.strftime('%X')}] Station is currently empty.")

            # Update our tracker for the next loop evaluation
            was_train_in_station = is_train_in_station_now

        except Exception as api_err:
            # Handle occasional network drops or MTA feed hiccups gracefully without crashing
            print(f"[{time.strftime('%X')}] MTA Feed Error: {api_err}")
        
        # The MTA updates its live data roughly every 30 seconds.
        # Checking every 15 seconds keeps your audio triggers highly responsive.
        time.sleep(15)

except KeyboardInterrupt:
    print("\nShutting down audio monitor system. Goodbye!")