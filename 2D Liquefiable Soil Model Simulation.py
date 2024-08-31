
# Created by Eng. MohammadReza Jalali Farahani, MS.c., - Sharif University Of technology, 2024
# Copyright © 2024 Eng. MohammadReza Jalali Farahani. All rights reserved.

#========================================================================================
#                               ****   Notes  ****
# This script simulates a 2D model of liquefiable soil using the OpenSeesPy framework
# You need to makes changes on the lines that. Please go through all the command lines before running it.
# Units are in Metric (kN, ton, sec, m). Check the units if you work with Imperial units. 
# The input motions should be available in two separate .txt files.
# Outputs will be saved in a folder titled "Outputs".
#========================================================================================

from openseespy.opensees import *
import math
import os
import sys

# Clear any previous model data
wipe()


#---------------------------------------------------
# User-defined variables for the model
#---------------------------------------------------

# Define node variables
numXele = 20       # Number of elements in the horizontal (x) direction
numYele = 10       # Number of elements in the vertical (y) direction
xSize = 1          # Element size in the x direction (m)
ySize = 1          # Element size in the y direction (m)
NumToTEle = numXele * numYele  # Total number of elements
numXnode = numXele + 1  # Number of nodes in the x direction
numYnode = numYele + 1  # Number of nodes in the y direction

#---------------------------------------------------
# Define material properties of soil
#---------------------------------------------------

# Define parameters for loose sand (Dr 50)
nod = 2.0                     # Number of dimensions (2D model)
satDensity = 1.9              # Saturated mass density (Mg/m³)
H2ODensity = 1.0              # Fluid mass density (Mg/m³)
shear = 10.0e4                # Shear modulus (kPa)
bulk1 = 23.3e4                # Bulk modulus (kPa)
FricAngel = 33.5              # Friction angle (degrees)
PeakShear = 0.1               # Peak shear strain
refPress = 101.0              # Reference pressure (kPa)
pressDependCoef = 0.5         # Pressure dependency coefficient
PTAngel = 25.5                # PT angle (degrees)
Cont1 = 0.045                 # Contact parameter 1
Cont2 = 5.0                   # Contact parameter 2
Cont3 = 0.15                  # Contact parameter 3
contrac = [Cont1, Cont2, Cont3]  # List of contact parameters
dilat1 = 0.06                 # Dilatancy parameter 1
dilat2 = 3.0                  # Dilatancy parameter 2
dilat3 = 0.25                 # Dilatancy parameter 3
dilat = [dilat1, dilat2, dilat3]  # List of dilatancy parameters
numSurf = 20                  # Number of yield surfaces
Liquefac1 = 1.0               # Liquefaction factor 1
Liquefac2 = 0.0               # Liquefaction factor 2
liquefac = [1.0, 0.0]         # List of liquefaction factors
e = 0.7                       # Porosity
Cs1 = 0.9                     # Parameter for defining ec
Cs2 = 0.02                    # Parameter for defining ec
Cs3 = 0.7                     # Parameter for defining ec
Pa = 101.0                    # Atmospheric pressure (kPa)
params = [0.9, 0.02, 0.7, 101.0]  # List of parameters

# Define element variables
bulk = 2.2e6 / e               # Fluid-solid combined bulk modulus
fmass = 1.0                    # Fluid mass density
INhperm = 100.0                # Initial horizontal permeability (m/s)
INvperm = 100.0                # Initial vertical permeability (m/s)
hPerm = 2.0e-3                 # Horizontal permeability (m/s)
vPerm = 2.0e-3                 # Vertical permeability (m/s)
accGravity = 9.81              # Acceleration due to gravity (m/s²)
loadBias = 0.0                 # Static shear load (percentage of gravity load)
pressure = 0.0                  # Isotropic consolidation pressure on quad elements
thick = 1.0                    # Element thickness (m)
deltaT = 0.1                   # Time step for analysis (s)

#---------------------
# Define Node
#---------------------
model('BasicBuilder', '-ndm', 2, '-ndf', 3)  # Initialize the model with 2D and 3 DOF per node

# Create nodes in a grid
for i in range(1, numXnode + 1):
    for j in range(1, numYnode + 1):
        xdim = (i - 1) * xSize  # X coordinate
        ydim = (j - 1) * ySize  # Y coordinate
        nodeNum = i + (j - 1) * numXnode  # Node number
        node(nodeNum, xdim, ydim)  # Create node
        print(f'Node {nodeNum}    {xdim}    {ydim}')  # Print node information

#---------------------
# Define Soil Material
#---------------------
matTag = 1  # Material tag for the soil
# Define the pressure-dependent multi-yield soil material
nDMaterial('PressureDependMultiYield02', matTag, nod, satDensity, shear, bulk1, FricAngel, PeakShear, 
           refPress, pressDependCoef, PTAngel, Cont1, Cont3, dilat1, dilat3, numSurf, Cont2, dilat2, 
           Liquefac1, Liquefac2, Cs3, Cs1, Cs2, e, Pa)

print("Finished creating all soil materials...")

#-------------------------------------------------------------------------------------------
# DEFINE ELEMENTS
#-------------------------------------------------------------------------------------------
# Create quadrilateral elements based on the nodes
for i in range(1, numXele + 1):
    for j in range(1, numYele + 1):
        eleTag = i + (j - 1) * numXele  # Element tag
        n1 = i + (j - 1) * numXnode  # Node 1
        n2 = i + (j - 1) * numXnode + 1  # Node 2
        n4 = i + j * numXnode + 1  # Node 4
        n3 = i + j * numXnode  # Node 3
        eleNodes = [n1, n2, n4, n3]  # List of nodes for the element
        # Create quadrilateral element with specified parameters
        element('quadUP', eleTag, *eleNodes, thick, matTag, bulk, fmass, 
                INhperm / accGravity / fmass, INvperm / accGravity / fmass, 0, -accGravity, 0)

#-----------------------------------------------------
# Update material stage to zero for elastic behavior
#-----------------------------------------------------
updateMaterialStage('-material', matTag, '-stage', 0)

#-----------------------------------------------------
# Resistance boundary condition
#-----------------------------------------------------
# Fix the base and allow free surface drainage
for i in range(1, numXnode + 1):
    fix(i, 1, 1, 0)  # Fix base nodes (x, y displacements)
    surfnode = (numYnode - 1) * numXnode + i  # Surface node number
    fix(surfnode, 0, 0, 1)  # Free drainage at the surface (fix z displacement)

#-----------------------------------------------------
# Tie all displacement DOFs at the same level
#-----------------------------------------------------
for i in range(1, numYnode):
    nodeNum1 = i * numXnode + 1  # First node in the row
    nodeNum2 = i * numXnode + numXnode  # Last node in the row
    equalDOF(nodeNum1, nodeNum2, 1, 2)  # Tie x and y displacements

print("Finished creating all soil elements...")

#-----------------------------------------------------
# APPLY GRAVITY LOADING
#-----------------------------------------------------
numberer("RCM")  # Set the numberer algorithm
system("ProfileSPD")  # Set the system of equations solver
test('NormDispIncr', 1.0e-2, 50, 0)  # Set convergence test
algorithm("KrylovNewton")  # Set the algorithm for solving
constraints('Penalty', 1e18, 1e18)  # Set constraints
gamma = 1.5  # Newmark integration parameter
beta = (gamma + 0.5) ** 2 / 4  # Newmark beta parameter
integrator('Newmark', gamma, beta)  # Set the integrator
analysis("Transient")  # Set analysis type to transient
analyze(10, 5e3)  # Perform analysis

print("Finished with elastic gravity analysis...")

#-----------------------------------------------------
# UPDATE SOIL MATERIAL STAGE
#-----------------------------------------------------
# Update material stage to consider elastoplastic behavior
updateMaterialStage('-material', matTag, '-stage', 1)

analyze(10, 1e1)  # Perform analysis for plastic behavior
# Re-zero time for the next analysis
wipeAnalysis()
setTime(0.0)  # Reset time to 0.0
print("Finished with plastic gravity analysis...")

#----------------------------------------------------
# Update parameters for permeability
#----------------------------------------------------
numLayers = 1.0  # Number of layers
ctr = 10000.0  # Base number for parameter IDs

# Create parameters for each element's permeability
for i in range(1, NumToTEle + 1):
    parameter(int(ctr + 1.0), 'element', i, 'vPerm')  # Vertical permeability parameter
    parameter(int(ctr + 2.0), 'element', i, 'hPerm')  # Horizontal permeability parameter
    ctr = ctr + 2.0  # Increment counter

# Update permeability parameters for each element using parameter IDs
ctr = 10000.0  # Reset counter
lowerBound = 0.0  # Lower bound for parameters
layerThick = 1  # Layer thickness
layerBound = layerThick  # Bound for layers

for j in range(1, NumToTEle + 1):  
    updateParameter(int(ctr + 1.0), vPerm / accGravity / fmass)  # Update vertical permeability
    updateParameter(int(ctr + 2.0), hPerm / accGravity / fmass)  # Update horizontal permeability
    ctr = ctr + 2.0  # Increment counter

print("Finished updating permeabilities for dynamic analysis...")

#-------------------------------------------------------------------------------------------
# CREATE RECORDERS
#-------------------------------------------------------------------------------------------
# Define nodes for recording results
nodeList1 = [53, 95, 137, 158, 179, 221]  # List of nodes to record data

# Create output directory if it doesn't exist
DataDir = "OutPuts"
if not os.path.exists(DataDir):
    os.makedirs(DataDir)

# Define recorders for displacement and pore pressure
recorder('Node', '-file', f'{DataDir}/disp2.txt', '-node', *nodeList1, '-time', '-dT', deltaT, '-dof', 1, 2, 'disp')
# Additional recorders can be uncommented as needed
recorder('Node', '-file', f'{DataDir}/Ydisp2.txt', '-node', *nodeList1, '-time', '-dT', deltaT, '-dof', 2, 'disp')
recorder('Node', '-file', f'{DataDir}/pwp1.txt', '-node', *nodeList1, '-time', '-dT', deltaT, '-dof', 3, 'vel')
recorder('Node', '-file', f'{DataDir}/acc1.txt', '-node', *nodeList1, '-time', '-dT', deltaT, '-dof', 1, 'accel')

# Define recorders for stress and strain in specific elements
recorder('Element', '-file', f'{DataDir}/stress10.txt', '-time', '-dT', deltaT, '-ele', 10, 'material', '1', 'stress')
recorder('Element', '-file', f'{DataDir}/strain10.txt', '-time', '-dT', deltaT, '-ele', 10, 'material', '1', 'strain')
recorder('Element', '-file', f'{DataDir}/stress70.txt', '-time', '-dT', deltaT, '-ele', 70, 'material', '1', 'stress')
recorder('Element', '-file', f'{DataDir}/strain70.txt', '-time', '-dT', deltaT, '-ele', 70, 'material', '1', 'strain')
recorder('Element', '-file', f'{DataDir}/stress130.txt', '-time', '-dT', deltaT, '-ele', 130, 'material', '1', 'stress')
recorder('Element', '-file', f'{DataDir}/strain130.txt', '-time', '-dT', deltaT, '-ele', 130, 'material', '1', 'strain')
recorder('Element', '-file', f'{DataDir}/stress190.txt', '-time', '-dT', deltaT, '-ele', 190, 'material', '1', 'stress')
recorder('Element', '-file', f'{DataDir}/strain190.txt', '-time', '-dT', deltaT, '-ele', 190, 'material', '1', 'strain')

print("Finished creating all recorders...")

#----------------------------------------
# Dynamic Analysis Setup
#----------------------------------------
# Base input motion setup
patternTag = 10  # Pattern tag for ground motion
accelSeriesTag = 1  # Time series tag for acceleration
direction = 1  # Direction of excitation (1 for x-direction)
GMPath = "acc_value.txt"  # Path to ground motion file

# Define the time series for acceleration input
timeSeries('Path', accelSeriesTag, '-dt', 0.01, '-filePath', GMPath, '-factor', accGravity)
# Create a uniform excitation pattern for the defined time series
pattern('UniformExcitation', accelSeriesTag, direction, '-accel', accelSeriesTag)

# Set up the analysis parameters
constraints('Transformation')  # Set transformation constraints
numberer('Plain')  # Set plain numberer
system('SparseSYM')  # Set sparse symmetric system
Tol = 1e-8  # Convergence test tolerance
maxNumIter = 10  # Maximum number of iterations for convergence test
printFlag = 1  # Flag for convergence test print
TestType = 'EnergyIncr'  # Type of convergence test
test(TestType, Tol, maxNumIter, printFlag)  # Set convergence test

# Set the algorithm for solving
algorithmType = 'KrylovNewton'
algorithm(algorithmType)

# Newmark integration parameters
NewmarkGamma = 0.5  # Gamma parameter for Newmark method
NewmarkBeta = 0.25  # Beta parameter for Newmark method
integrator('Newmark', NewmarkGamma, NewmarkBeta)  # Set the integrator
analysis('Transient')  # Set analysis type to transient

#--- RAYLEIGH DAMPING PARAMETERS ---
pi = 3.141592654  # Value of pi
damp = 0.02  # Damping ratio
omega1 = 2 * pi * 1  # Lower frequency (rad/s)
omega2 = 2 * pi * 20  # Upper frequency (rad/s)
# Calculate Rayleigh damping coefficients
a0 = 2 * damp * omega1 * omega2 / (omega1 + omega2)  # Damping coefficient a0
a1 = 2 * damp / (omega1 + omega2)  # Damping coefficient a1
print(f"damping coefficients: a_0 = {a0};  a_1 = {a1}")  # Print damping coefficients
rayleigh(a0, a1, 0.0, 0.0)  # Apply Rayleigh damping

# Perform analysis with timestep reduction loop
dT = 0.0025  # Initial time step for analysis
nSteps = 13000  # Total number of time steps
ok = analyze(nSteps, dT)  # Perform analysis

# If analysis fails, reduce timestep and continue
if ok != 0:
    print("did not converge, reducing time step")
    curTime = getTime()  # Get current simulation time
    mTime = curTime  # Store current time
    print(f'curTime: {curTime}')
    curStep = curTime / dT  # Current step number
    print(f'curStep: {curStep}')
    rStep = (nSteps - curStep) * 2.0  # Remaining steps to take
    remStep = int((nSteps - curStep) * 2.0)  # Convert to integer
    print(f'remStep: {remStep}')
    dT = dT / 2.0  # Reduce time step
    print(f'dT: {dT}')

    ok = analyze(remStep, dT)  # Continue analysis with reduced timestep

   # if analysis fails again, reduce timestep and continue with analysis
    if ok != 0 :
        print("did not converge, reducing time step")
        curTime =getTime()
        print(f'curTime: {curTime}')
        curStep  = (curTime-mTime)/dT
        print(f'curStep: {curStep}')
        remStep = int((rStep-curStep)*2.0)
        print(f'remStep: {remStep}')
        dT      = dT/2.0
        print(f'dT: {dT}')

        ok = analyze(remStep ,dT)

print("Finished with dynamic analysis...")
wipe()
