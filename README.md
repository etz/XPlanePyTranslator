# XPlanePyTranslator

XPlanePyTranslator allows you to extract data from X-Plane 11 and convert the data to a python dictionary, where it can be used for various functions such as flight recording and playback, actuation of servos, or the generation of new packets given a dictionary provided in the same format they are generated. Basically, XPlanePyTranslator allows a user to read or write data to X-Plane and create their own scripts for outgoing data.

*Note: This only works with general data outputs, not datarefs.*


# Included scripts

[Actuation/actuate.py](Actuation/actuate.py): Actuates small servos found in retail RC planes using a Servo Driver HAT and a Raspberry Pi Zero W.

[Flight Record & Playback/recorder.py](Flight Record%20%26%20Playback/recorder.py): Reads X-Plane data, converts to hex, and stores in a file associated with the time of the simulated flight for future playback.

[Flight Record & Playback/controller.py](Flight Record%20%26%20Playback/controller.py): Reads from a script generated using recorder.py and sends it to X-Plane 11, allowing for a flight to be replayed without the use of the replayer (given specific values being recorded)

## TODO

Finish the generation script

# Credits & Acknowledgements
This project was created for Embry-Riddle Aeronautical University as part of a sponsored research project in collaboration with the Department of Defense.
