import time
from pygame import mixer
from nyct_gtfs import NYCTFeed

# 1. Initialize Audio
mixer.init()
try:
    arrival_sound = mixer.Sound("ArrivalLong.mp3")
    departure_sound = mixer.Sound("Departure.mp3")
except Exception as e:
    print(f"Error loading audio files: {e}")
    print("Make sure 'arrival.mp3' and 'departure.mp3' are in this folder.")
    exit()

# 2. MTA Configuration
FEED_LINE = "1"
TARGET_STOP = "117S"  # 137th St - Downtown (Southbound)

# State tracking variable to detect transitions
was_train_in_station = False

print("Starting Subway Audio Monitor System...")

try:
    while True:
        try:
            feed = NYCTFeed(FEED_LINE)
            trains = feed.filter_trips(stop_id=TARGET_STOP, underway=True)
            
            is_train_in_station_now = False
            
            for train in trains:
                status = train.current_status
                current_stop = train.current_stop_id
                
                if status == "STOPPED_AT" and current_stop == TARGET_STOP:
                    is_train_in_station_now = True
                    break

            # --- State Transition Logic ---
            
            # Case A: Train just arrived (It wasn't there before, but it is now)
            if is_train_in_station_now and not was_train_in_station:
                print("[ARRIVED] Downtown 1 train has entered 137th St. Playing sound...")
                arrival_sound.play()
                
            # Case B: Train just left (It was there before, but it isn't now)
            elif not is_train_in_station_now and was_train_in_station:
                print("[DEPARTED] Train has left 137th St. Playing sound...")
                departure_sound.play()
                
            else:
                # No change in state
                if is_train_in_station_now:
                    print("Train is still stopped at the platform...")
                else:
                    print("Station is currently empty.")

            # Update our tracker for the next loop
            was_train_in_station = is_train_in_station_now

        except Exception as api_err:
            print(f"MTA Feed Error: {api_err}")
        
        # Check every 15 seconds for snappier audio response
        time.sleep(15)

except KeyboardInterrupt:
    print("\nShutting down audio monitor.")