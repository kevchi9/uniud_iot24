import beamngpy
import time
import pickle

if __name__ == "__main__":
    beamng = beamngpy.BeamNGpy('localhost', 64256, home= 'home_path', user = 'user_path')
    beamng.open()

    scenario = beamngpy.Scenario('hirochi_raceway', 'telem')
    ego = beamngpy.Vehicle('ego', model='sunburst', color='White', licence='PYTHON')

    imu = beamngpy.sensors.IMU(pos=(0.73, 0.51, 0.8))
    electrics = beamngpy.sensors.Electrics()
    damage = beamngpy.sensors.Damage()
    timer = beamngpy.sensors.Timer()
    ego.attach_sensor('imu', imu)
    ego.attach_sensor('electrics', electrics)
    ego.attach_sensor('damage', damage)
    ego.attach_sensor('timer', timer)

    scenario.add_vehicle(ego, pos=(-382, 221, 25.5), rot_quat=(0,0,1,-1))
    scenario.make(beamng)
    beamng.load_scenario(scenario)
    beamng.start_scenario()

    start = time.time()
    duration = 600
    end_iteration = time.time()
    telem = {}
    i = 0
    j=0
    while (end_iteration-start < duration):
        begin_iteration = time.time()
        ego.poll_sensors()

        new_obj = {}
        for entry in ego.sensors:
            new_obj[entry] = ego.sensors[entry].data

        telem[begin_iteration] = new_obj

        end_iteration = time.time()
        diff = end_iteration - begin_iteration
        if diff < 0.045:
            time.sleep(0.045 - (end_iteration-begin_iteration))
        else:
            print(diff)

    with open('telemetry.pickle', 'wb') as outfile:
        pickle.dump(telem, outfile, protocol=pickle.HIGHEST_PROTOCOL)