Objects:

Plant:
    Fields:
- current_moisture (float)
- minimum_moisture (float)
- last_watering(time)


Watersystem: 

    Fields: 
    - watering_history(array of timestamps, maybe more infos, linke moinsturevalue)

    Functions: 
    - watering()
        -> water the plant, until current_moinsture is minimum_moinsture or above
        -> 
    - check_last_watering()

Ideas watering():

issues: 
- sensor does not pick up the new watering right away -> time between watering
- what if the sensor is not working properly? (failproof, should not water all the time in that case) ->stop programm, when strange value accures 
- 


- incemental: (1) check moist, if current_moisture<minimum_moisture, do 2. (2) : water a constant amout (small amout, so water will be recognized by the sensor)
 



Questions: 

- how much time should be there between watering? (time it takes till the sensor can accuratly tell the moinsuring)
- is there a difference between plants, how big the window between watering shoud be? 


