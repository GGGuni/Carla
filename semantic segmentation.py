import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import random
import time

def main():
    actor_list = []

    try:
        #create client (send the requests to the simulator)
        client = carla.Client('localhost',2000)
        client.set_timeout(2.0)
	
	#retrieve world
        world = client.get_world()

	#blueprints : adding new actors
        blueprint_library = world.get_blueprint_library()

        bp = random.choice(blueprint_library.filter('vehicle'))
	
	#random color
        if bp.has_attribute('color'):
            color = random.choice(bp.get_attribute('color').recommended_values)
            bp.set_attribute('color', color)
	
	#random spwan point
        transform = random.choice(world.get_map().get_spawn_points())
	
	#spawn vehicle
        vehicle = world.spawn_actor(bp, transform)
	
	#나중에 한번에 지우기 위해 모든 물체들 저장
        actor_list.append(vehicle)
        print('created %s' % vehicle.type_id)

	#vehicle drive
        vehicle.set_autopilot(True)

	#"depth" camera vehicle에 붙이기(자동차마다 상대적)
        camera_bp = blueprint_library.find('sensor.camera.semantic_segmentation')
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        actor_list.append(camera)
        print('created %s' % camera.type_id)

	#sensor가 이미지를 얼마나 자주 받아옴?
	#이미지를 어디에 저장?
        #cc = carla.ColorConverter.LogarithmicDepth
        camera.listen(lambda image: image.save_to_disk('semantic_out/%06d.png' %image.frame, carla.ColorConverter.CityScapesPalette ))
	
	#vehicle 추가
        transform.location += carla.Location(x=40, y=-3.2)
        transform.rotation.yaw = -180.0
        for _ in range(0, 10):
            transform.location.x += 8.0

            bp = random.choice(blueprint_library.filter('vehicle'))

            # This time we are using try_spawn_actor. If the spot is already
            # occupied by another object, the function will return None.
            npc = world.try_spawn_actor(bp, transform)
            if npc is not None:
                actor_list.append(npc)
                npc.set_autopilot(True)
                print('created %s' % npc.type_id)

        time.sleep(5)

    finally:	
        print('destroying actors')
        camera.destroy()
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        print('done.')


if __name__ == '__main__':
	main()

	

	






	
