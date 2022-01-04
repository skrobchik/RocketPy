# -*- coding: utf-8 -*-

__author__ = ""
__copyright__ = "Copyright 20XX, Projeto Jupiter"
__license__ = "MIT"


from datetime import datetime
from os import _Environ
from time import process_time, perf_counter, time
import glob


import numpy as np
from numpy.random import normal, uniform, choice
from IPython.display import display
from rocketpy.Environment import Environment
import matplotlib.pyplot as plt
from imageio import imread
from matplotlib.patches import Ellipse

from rocketpy.Flight import Flight
from rocketpy.Function import Function

class Analysis:
    '''
    
    Documentation
    
    '''

    def __init__(
        self,
        env,
        motor,
        rocket,
        flight
    ):
        self.env = env
        self.motor = motor
        self.rocket = rocket
        self.flight = flight


    def dispersionData(
        self,
        rocketMassSD,
        impulseSD,
        burnOutSD,
        nozzleRadiusSD,
        throatRadiusSD,
        grainSeparationSD,
        grainDensitySD,
        grainOuterRadiusSD,
        grainInitialInnerRadiusSD,
        grainInitialHeightSD,
        inertiaISD,
        inertiaZSD,
        radiusSD,
        distanceRocketNozzleSD,
        distanceRocketPropellantSD,
        powerOffDragSD,
        powerOnDragSD,
        noseLengthSD,
        noseDistanceToCMSD,
        finSpanSD,
        finRootChordSD,
        finTipChordSD,
        finDistanceToCMSD,
        inclinationSD,
        headingSD,
        railLengthSD,
        ensembleMemberRange,
        CdS_SD,
        lag_recSD,
        lag_seSD,
        number_of_simulations
    ):
        analysis_parameters = {
            "rocket.mass":(self.rocket.mass,rocketMassSD),
            "impulse":(self.motor.totalImpulse,impulseSD),
            "burnOut": (self.motor.burnOut,burnOutSD),
            "nozzleRadius":(self.motor.nozzleRadius,nozzleRadiusSD),
            "throatRadius":(self.motor.throatRadius,throatRadiusSD),
            "grainSeparation":(self.motor.grainSeparation,grainSeparationSD),
            "grainDensity":(self.motor.grainDensity,grainDensitySD),
            "grainOuterRadius":(self.motor.grainOuterRadius,grainOuterRadiusSD),
            "grainInitialInnerRadius":(self.motor.grainInitialInnerRadius,grainInitialInnerRadiusSD),
            "grainInitialHeight":(self.motor.grainInitialHeight,grainInitialHeightSD),
            "inertiaI":(self.rocket.inertiaI,inertiaISD),
            "inertiaZ":(self.rocket.inertiaZ,inertiaZSD),
            "radius":(self.rocket.radius,radiusSD),
            "distanceRocketNozzle":(self.rocket.distanceRocketNozzle,distanceRocketNozzleSD),
            "distanceRocketPropellant":(self.rocket.distanceRocketPropellant,distanceRocketPropellantSD),
            "powerOffDrag":(self.rocket.powerOffDrag,powerOffDragSD),
            "powerOnDrag":(self.rocket.powerOnDrag,powerOnDragSD),
            "noseLength":(self.rocket.noseLength,noseLengthSD),
            "noseDistanceToCM":(self.rocket.noseDistanceToCM,noseDistanceToCMSD),
            "finSpan":(self.rocket.span,finSpanSD),
            "finRootChord":(self.rocket.rootChord,finRootChordSD),
            "finTipChord":(self.rocket.tipChord,finTipChordSD),
            "finDistanceToCM":(self.rocket.distanceToCM,finDistanceToCMSD),
            "inclination":(self.flight.inclination,inclinationSD),
            "heading":(self.flight.heading,headingSD),
            "railLength":(self.env.railLength,railLengthSD),
            "ensembleMember":(self.env.ensembleMember,ensembleMemberRange),
            "CdS":(self.rocket.CdS,CdS_SD),
            "lag_rec":(self.rocket.lag,lag_recSD),
            "lag_se":(self.rocket.lag_se,lag_seSD)                 #?
        }
        
        i = 0
        while i < number_of_simulations:
            # Generate a flight setting
            flight_setting = {}
            for parameter_key, parameter_value in analysis_parameters.items():
                if type(parameter_value) is tuple:
                    flight_setting[parameter_key] =  normal(*parameter_value)
                else:
                    flight_setting[parameter_key] =  choice(parameter_value)

            # Skip if certain values are negative, which happens due to the normal curve but isnt realistic
            if flight_setting['lag_rec'] < 0 or  flight_setting['lag_se'] < 0: continue
                
            # Update counter
            i += 1
            # Yield a flight setting
            yield flight_setting

        # Basic analysis info
        filename = 'dispersion_analysis_outputs/rocket_v0'

        # Create data files for inputs, outputs and error logging
        dispersion_error_file = open(str(filename)+'.disp_errors.txt', 'w')
        dispersion_input_file = open(str(filename)+'.disp_inputs.txt', 'w')
        dispersion_output_file = open(str(filename)+'.disp_outputs.txt', 'w')

        # Initialize counter and timer
        i = 0

        initial_wall_time = time()
        initial_cpu_time = process_time()


        # Iterate over flight settings
        out = display('Starting', display_id=True)
        for setting in flight_setting: 
            start_time = process_time()
            i += 1
                
            # Create environment 
            envDispersion = Environment(
                railLenght=(setting['railLength']),
                gravity=9.80665,
                date=self.env.date,
                latitude=self.env.latitude,
                longitude=self.env.longitude,
                elevation=self.env.elevation,
                datum=self.env.datum
            )
            envDispersion.selectEnsembleMember(setting['ensembleMember'])
            

            # Create motor
            motorDispersion = Motor(
                thrustSource=self.motor.thrustSource,
                burnOut=setting['burnOut'],
                reshapeThrustCurve=(setting['burnOut'], setting['impulse']),
                nozzleRadius=setting['nozzleRadius'],
                throatRadius=setting['throatRadius'],
                grainNumber=self.motor.grainNumber,
                grainSeparation=setting['grainSeparation'],
                grainDensity=setting['grainDensity'],
                grainOuterRadius=setting['grainOuterRadius'],
                grainInitialInnerRadius=setting['grainInitialInnerRadius'],
                grainInitialHeight=setting['grainInitialHeight'],
                interpolationMethod='linear'
            )
            
            # Create rocket
            rocketDispersion = Rocket(
                motor=motorDispersion,
                radius=setting['radius'],
                mass=setting['rocketMass'],
                inertiaI=setting['inertiaI'],
                inertiaZ=setting['inertiaZ'],
                distanceRocketNozzle=setting['distanceRocketNozzle'],
                distanceRocketPropellant=setting['distanceRocketPropellant'],
                powerOffDrag=self.rocket.powerOffDrag * setting["powerOffDrag"],
                powerOnDrag=self.rocket.powerOnDrag * setting["powerOnDrag"]
            )
            
            # Add rocket nose, fins and tail
            rocketDispersion.addNose(
                length=setting['noseLength'],
                kind=self.rocket.kind,
                distanceToCM=setting['noseDistanceToCM']
            )
            rocketDispersion.addFins(
                n=self.rocket.n,
                rootChord=setting['finRootChord'],
                tipChord=setting['finTipChord'],
                span=setting['finSpan'],
                distanceToCM=setting['finDistanceToCM']
            )
            # Add parachute
            rocketDispersion.addParachute(
                self.rocket.name,
                CdS=setting['CdSDrogue'],
                trigger=self.rocket.trigger, 
                samplingRate=self.rocket.samplingRate,
                lag=setting['lag_rec'] + setting['lag_se'],
                noise=self.rocket.noise
            )

            # Run trajectory simulation
            try:
                TestFlight = Flight(
                    rocket=rocketDispersion,
                    environment=envDispersion,
                    inclination=setting['inclination'],
                    heading=setting['heading'],
                    maxTime=600
                )
                
                # Generate flight results
                flight_result = {"outOfRailTime": TestFlight.outOfRailTime,
                    "outOfRailVelocity": TestFlight.outOfRailVelocity,
                    "apogeeTime": TestFlight.apogeeTime,
                    "apogeeAltitude": TestFlight.apogee - envDispersion.elevation,
                    "apogeeX": TestFlight.apogeeX,
                    "apogeeY": TestFlight.apogeeY,
                    "impactTime": TestFlight.tFinal,
                    "impactX": TestFlight.xImpact,
                    "impactY": TestFlight.yImpact,
                    "impactVelocity": TestFlight.impactVelocity,
                    "initialStaticMargin": TestFlight.rocket.staticMargin(0),
                    "outOfRailStaticMargin": TestFlight.rocket.staticMargin(TestFlight.outOfRailTime),
                    "finalStaticMargin": TestFlight.rocket.staticMargin(TestFlight.rocket.motor.burnOutTime),
                    "numberOfEvents": len(TestFlight.parachuteEvents),
                    "executionTime": process_time() - start_time
                }
                
                # Calculate maximum reached velocity
                sol = np.array(TestFlight.solution)
                TestFlight.vx = Function(sol[:, [0, 4]], 'Time (s)', 'Vx (m/s)', 'linear', extrapolation="natural")
                TestFlight.vy = Function(sol[:, [0, 5]], 'Time (s)', 'Vy (m/s)', 'linear', extrapolation="natural")
                TestFlight.vz = Function(sol[:, [0, 6]], 'Time (s)', 'Vz (m/s)', 'linear', extrapolation="natural")
                TestFlight.v = (TestFlight.vx**2 + TestFlight.vy**2 + TestFlight.vz**2)**0.5
                TestFlight.maxVel = np.amax(TestFlight.v.source[:, 1])
                flight_result['maxVelocity'] = TestFlight.maxVel
                
                # Take care of parachute results
                if len(TestFlight.parachuteEvents) > 0:
                    flight_result['drogueTriggerTime'] = TestFlight.parachuteEvents[0][0]
                    flight_result['drogueInflatedTime'] = TestFlight.parachuteEvents[0][0] + TestFlight.parachuteEvents[0][1].lag
                    flight_result['drogueInflatedVelocity'] = TestFlight.v(TestFlight.parachuteEvents[0][0] + TestFlight.parachuteEvents[0][1].lag)
                else:
                    flight_result['drogueTriggerTime'] = 0
                    flight_result['drogueInflatedTime'] = 0
                    flight_result['drogueInflatedVelocity'] = 0
                
                # Write flight setting and results to file
                dispersion_input_file.write(str(setting) + '\n')
                dispersion_output_file.write(str(flight_result) + '\n')

            except Exception as E:
                print(E)
                dispersion_error_file.write(str(setting) + '\n')

            # Register time
            out.update(f"Curent iteration: {i:06d} | Average Time per Iteration: {(process_time() - initial_cpu_time)/i:2.6f} s")

        # Done

        ## Print and save total time
        final_string = f"Completed {i} iterations successfully. Total CPU time: {process_time() - initial_cpu_time} s. Total wall time: {time() - initial_wall_time} s"
        out.update(final_string)
        dispersion_input_file.write(final_string + '\n')
        dispersion_output_file.write(final_string + '\n')
        dispersion_error_file.write(final_string + '\n')

        ## Close files
        dispersion_input_file.close()
        dispersion_output_file.close()
        dispersion_error_file.close()
    
    def importingDispersionResultsFromFile(self,dispersion_output_file):
        
        # Initialize variable to store all results
        dispersion_general_results = []

        dispersion_results = {"outOfRailTime": [],
                          "outOfRailVelocity": [],
                                 "apogeeTime": [],
                             "apogeeAltitude": [],
                                    "apogeeX": [],
                                    "apogeeY": [],
                                 "impactTime": [],
                                    "impactX": [],
                                    "impactY": [],
                             "impactVelocity": [],
                        "initialStaticMargin": [],
                      "outOfRailStaticMargin": [],
                          "finalStaticMargin": [],
                             "numberOfEvents": [],
                                "maxVelocity": [],
                       "parachuteTriggerTime": [],
                      "parachuteInflatedTime": [],
                  "parachuteInflatedVelocity": [],
                              "executionTime": []}

        # Get all dispersion results
        # Get file
        dispersion_output_file = open(dispersion_output_file, 'r+')

        # Read each line of the file and convert to dict
        for line in dispersion_output_file:
            # Skip comments lines
            if line[0] != '{': continue
            # Eval results and store them
            flight_result = eval(line)
            dispersion_general_results.append(flight_result)
            for parameter_key, parameter_value in flight_result.items():
                dispersion_results[parameter_key].append(parameter_value)

        # Close data file
        dispersion_output_file.close()

        # Print number of flights simulated
        return dispersion_results

    def plotOutOfRailTime(self,dispersion_results):
        print(f'Out of Rail Time -         Mean Value: {np.mean(dispersion_results["outOfRailTime"]):0.3f} s')
        print(f'Out of Rail Time - Standard Deviation: {np.std(dispersion_results["outOfRailTime"]):0.3f} s')

        plt.figure()
        plt.hist(dispersion_results["outOfRailTime"], bins=int(N**0.5))
        plt.title('Out of Rail Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None

    def plotOutOfRailVelocity(self,dispersion_results):
        print(f'Out of Rail Velocity -         Mean Value: {np.mean(dispersion_results["outOfRailVelocity"]):0.3f} m/s')
        print(f'Out of Rail Velocity - Standard Deviation: {np.std(dispersion_results["outOfRailVelocity"]):0.3f} m/s')

        plt.figure()
        plt.hist(dispersion_results["outOfRailVelocity"], bins=int(N**0.5))
        plt.title('Out of Rail Velocity')
        plt.xlabel('Velocity (m/s)')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None

    def plotApogeeTime(self,dispersion_results):
        print(f'Impact Time -         Mean Value: {np.mean(dispersion_results["impactTime"]):0.3f} s')
        print(f'Impact Time - Standard Deviation: {np.std(dispersion_results["impactTime"]):0.3f} s')

        plt.figure()
        plt.hist(dispersion_results["impactTime"], bins=int(N**0.5))
        plt.title('Impact Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None

    def plotApogeeAltitude(self,dispersion_results):
        print(f'Apogee Altitude -         Mean Value: {np.mean(dispersion_results["apogeeAltitude"]):0.3f} m')
        print(f'Apogee Altitude - Standard Deviation: {np.std(dispersion_results["apogeeAltitude"]):0.3f} m')

        plt.figure()
        plt.hist(dispersion_results["apogeeAltitude"], bins=int(N**0.5))
        plt.title('Apogee Altitude')
        plt.xlabel('Altitude (m)')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None

    def plotApogeeXPosition(self,dispersion_results):
        print(f'Apogee X Position -         Mean Value: {np.mean(dispersion_results["apogeeX"]):0.3f} m')
        print(f'Apogee X Position - Standard Deviation: {np.std(dispersion_results["apogeeX"]):0.3f} m')

        plt.figure()
        plt.hist(dispersion_results["apogeeX"], bins=int(N**0.5))
        plt.title('Apogee X Position')
        plt.xlabel('Apogee X Position (m)')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None

    def plotApogeeYPosition(self,dispersion_results):
        print(f'Apogee Y Position -         Mean Value: {np.mean(dispersion_results["apogeeY"]):0.3f} m')
        print(f'Apogee Y Position - Standard Deviation: {np.std(dispersion_results["apogeeY"]):0.3f} m')

        plt.figure()
        plt.hist(dispersion_results["apogeeY"], bins=int(N**0.5))
        plt.title('Apogee Y Position')
        plt.xlabel('Apogee Y Position (m)')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None

    def plotImpactTime(self,dispersion_results):
        print(f'Impact Time -         Mean Value: {np.mean(dispersion_results["impactTime"]):0.3f} s')
        print(f'Impact Time - Standard Deviation: {np.std(dispersion_results["impactTime"]):0.3f} s')

        plt.figure()
        plt.hist(dispersion_results["impactTime"], bins=int(N**0.5))
        plt.title('Impact Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None

    def plotImpactXPosition(self,dispersion_results):
        print(f'Impact X Position -         Mean Value: {np.mean(dispersion_results["impactX"]):0.3f} m')
        print(f'Impact X Position - Standard Deviation: {np.std(dispersion_results["impactX"]):0.3f} m')

        plt.figure()
        plt.hist(dispersion_results["impactX"], bins=int(N**0.5))
        plt.title('Impact X Position')
        plt.xlabel('Impact X Position (m)')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None

    def plotImpactYPosition(self,dispersion_results):
        print(f'Impact Y Position -         Mean Value: {np.mean(dispersion_results["impactY"]):0.3f} m')
        print(f'Impact Y Position - Standard Deviation: {np.std(dispersion_results["impactY"]):0.3f} m')

        plt.figure()
        plt.hist(dispersion_results["impactY"], bins=int(N**0.5))
        plt.title('Impact Y Position')
        plt.xlabel('Impact Y Position (m)')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None

    def plotImpactVelocity(self,dispersion_results):
        print(f'Impact Velocity -         Mean Value: {np.mean(dispersion_results["impactVelocity"]):0.3f} m/s')
        print(f'Impact Velocity - Standard Deviation: {np.std(dispersion_results["impactVelocity"]):0.3f} m/s')

        plt.figure()
        plt.hist(dispersion_results["impactVelocity"], bins=int(N**0.5))
        plt.title('Impact Velocity')
        plt.xlim(-35,0)
        plt.xlabel('Velocity (m/s)')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None

    def plotStaticMargin(self,dispersion_results):
        print(f'Initial Static Margin -             Mean Value: {np.mean(dispersion_results["initialStaticMargin"]):0.3f} c')
        print(f'Initial Static Margin -     Standard Deviation: {np.std(dispersion_results["initialStaticMargin"]):0.3f} c')

        print(f'Out of Rail Static Margin -         Mean Value: {np.mean(dispersion_results["outOfRailStaticMargin"]):0.3f} c')
        print(f'Out of Rail Static Margin - Standard Deviation: {np.std(dispersion_results["outOfRailStaticMargin"]):0.3f} c')

        print(f'Final Static Margin -               Mean Value: {np.mean(dispersion_results["finalStaticMargin"]):0.3f} c')
        print(f'Final Static Margin -       Standard Deviation: {np.std(dispersion_results["finalStaticMargin"]):0.3f} c')

        plt.figure()
        plt.hist(dispersion_results["initialStaticMargin"], label='Initial', bins=int(N**0.5))
        plt.hist(dispersion_results["outOfRailStaticMargin"], label='Out of Rail', bins=int(N**0.5))
        plt.hist(dispersion_results["finalStaticMargin"], label='Final', bins=int(N**0.5))
        plt.legend()
        plt.title('Static Margin')
        plt.xlabel('Static Margin (c)')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None

    def plotMaximumVelocity(self,dispersion_results):
        print(f'Maximum Velocity -         Mean Value: {np.mean(dispersion_results["maxVelocity"]):0.3f} m/s')
        print(f'Maximum Velocity - Standard Deviation: {np.std(dispersion_results["maxVelocity"]):0.3f} m/s')

        plt.figure()
        plt.hist(dispersion_results["maxVelocity"], bins=int(N**0.5))
        plt.title('Maximum Velocity')
        plt.xlabel('Velocity (m/s)')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None
    
    def plotNumberOfParachuteEvents(self,dispersion_results):
        plt.figure()
        plt.hist(dispersion_results["numberOfEvents"])
        plt.title('Parachute Events')
        plt.xlabel('Number of Parachute Events')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None

    def plotParachuteTriggerTime(self,dispersion_results):
        print(f'Parachute Trigger Time -         Mean Value: {np.mean(dispersion_results["parachuteTriggerTime"]):0.3f} s')
        print(f'Parachute Trigger Time - Standard Deviation: {np.std(dispersion_results["parachuteTriggerTime"]):0.3f} s')

        plt.figure()
        plt.hist(dispersion_results["parachuteTriggerTime"], bins=int(N**0.5))
        plt.title('Parachute Trigger Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None

    def plotParachuteFullyInflatedTime(self,dispersion_results):
        print(f'Parachute Fully Inflated Time -         Mean Value: {np.mean(dispersion_results["parachuteInflatedTime"]):0.3f} s')
        print(f'Parachute Fully Inflated Time - Standard Deviation: {np.std(dispersion_results["parachuteInflatedTime"]):0.3f} s')

        plt.figure()
        plt.hist(dispersion_results["parachuteInflatedTime"], bins=int(N**0.5))
        plt.title('Parachute Fully Inflated Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Number of Occurences')
        plt.show()

        return None

    def plotParachuteFullyVelocity(self,dispersion_results):
        print(f'Drogue Parachute Fully Inflated Velocity -         Mean Value: {np.mean(dispersion_results["parachuteInflatedVelocity"]):0.3f} m/s')
        print(f'Drogue Parachute Fully Inflated Velocity - Standard Deviation: {np.std(dispersion_results["parachuteInflatedVelocity"]):0.3f} m/s')

        plt.figure()
        plt.hist(dispersion_results["parachuteInflatedVelocity"], bins=int(N**0.5))
        plt.title('Drogue Parachute Fully Inflated Velocity')
        plt.xlabel('Velocity m/s)')
        plt.ylabel('Number of Occurences')
        plt.show()
        
        return None

    def plotEllipses(self):
        
        # Import background map
        img = imread("dispersion_analysis_inputs/Valetudo_basemap_final.jpg")

        # Retrieve dispersion data por apogee and impact XY position
        apogeeX = np.array(dispersion_results['apogeeX'])
        apogeeY = np.array(dispersion_results['apogeeY'])
        impactX = np.array(dispersion_results['impactX'])
        impactY = np.array(dispersion_results['impactY'])

        # Define function to calculate eigen values
        def eigsorted(cov):
            vals, vecs = np.linalg.eigh(cov)
            order = vals.argsort()[::-1]
            return vals[order], vecs[:,order]
        
        # Create plot figure
        plt.figure(num=None, figsize=(8, 6), dpi=150, facecolor='w', edgecolor='k')
        ax = plt.subplot(111)

        # Calculate error ellipses for impact
        impactCov = np.cov(impactX, impactY)
        impactVals, impactVecs = eigsorted(impactCov)
        impactTheta = np.degrees(np.arctan2(*impactVecs[:,0][::-1]))
        impactW, impactH = 2 * np.sqrt(impactVals)

        # Draw error ellipses for impact
        impact_ellipses = []
        for j in [1, 2, 3]:
            impactEll = Ellipse(xy=(np.mean(impactX), np.mean(impactY)),
                        width=impactW*j, height=impactH*j,
                        angle=impactTheta, color='black')
            impactEll.set_facecolor((0, 0, 1, 0.2))
            impact_ellipses.append(impactEll)
            ax.add_artist(impactEll)

        # Calculate error ellipses for apogee
        apogeeCov = np.cov(apogeeX, apogeeY)
        apogeeVals, apogeeVecs = eigsorted(apogeeCov)
        apogeeTheta = np.degrees(np.arctan2(*apogeeVecs[:,0][::-1]))
        apogeeW, apogeeH = 2 * np.sqrt(apogeeVals)

        # Draw error ellipses for apogee
        for j in [1, 2, 3]:
            apogeeEll = Ellipse(xy=(np.mean(apogeeX), np.mean(apogeeY)),
                        width=apogeeW*j, height=apogeeH*j,
                        angle=apogeeTheta, color='black')
            apogeeEll.set_facecolor((0, 1, 0, 0.2))
            ax.add_artist(apogeeEll)
            
        # Draw launch point
        plt.scatter(0, 0, s=30, marker='*', color='black', label='Launch Point')
        # Draw apogee points
        plt.scatter(apogeeX, apogeeY, s=5, marker='^', color='green', label='Simulated Apogee') 
        # Draw impact points
        plt.scatter(impactX, impactY, s=5, marker='v', color='blue', label='Simulated Landing Point')
        # Draw real landing point
        plt.scatter(411.89, -61.07, s=20, marker='X', color='red', label='Measured Landing Point')

        plt.legend()

        # Add title and labels to plot
        ax.set_title('1$\sigma$, 2$\sigma$ and 3$\sigma$ Dispersion Ellipses: Apogee and Lading Points')
        ax.set_ylabel('North (m)')
        ax.set_xlabel('East (m)')

        # Add background image to plot
        # You can translate the basemap by changing dx and dy (in meters)
        dx = 0
        dy = 0
        plt.imshow(img,zorder=0, extent=[-1000-dx, 1000-dx, -1000-dy, 1000-dy])
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.xlim(-100, 700)
        plt.ylim(-300, 300)

        # Save plot and show result
        plt.savefig(str(filename)+ '.pdf', bbox_inches='tight', pad_inches=0)
        plt.savefig(str(filename)+ '.svg', bbox_inches='tight', pad_inches=0)
        plt.show()

    def plotOutOfRailVelocityByMass(self,minMass,maxMass,numPoints):

        def outOfRailVelocity(mass):
            self.rocket.mass = mass
            newMassFlight = Flight(self.rocket,self.env,inclination=80, heading=90, initialSolution=None, terminateOnApogee=False, maxTime=600, maxTimeStep=np.inf, minTimeStep=0, rtol=0.000001, atol=6 * [0.001] + 4 * [0.000001] + 3 * [0.001], timeOvershoot=True, verbose=False)
            return newMassFlight.outOfRailVelocity

        outOfRailVelocityByMass = Function(outOfRailVelocity,inputs='Mass (kg)',outputs='Out of Rail Velocity (m/s)')
        outOfRailVelocityByMass.plot(minMass,maxMass,numPoints)

        return None
