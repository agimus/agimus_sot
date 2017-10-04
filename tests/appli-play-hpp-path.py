#from dynamic_graph.sot.core.meta_task_posture import MetaTaskKinePosture
from dynamic_graph.sot.core.matrix_util import matrixToTuple
from numpy import eye

from dynamic_graph.sot.core import Task, FeatureGeneric, GainAdaptive
from dynamic_graph.sot.core.meta_tasks import setGain
from dynamic_graph.sot.core.matrix_util import matrixToTuple
from dynamic_graph.sot.hpp import PathSampler
from numpy import identity, hstack, zeros

# Create the posture task
task_name = "posture_task"
taskPosture = Task(task_name)
taskPosture.dyn = robot.dynamic
taskPosture.feature = FeatureGeneric('feature_'+task_name)
taskPosture.featureDes = FeatureGeneric('feature_des_'+task_name)
taskPosture.gain = GainAdaptive("gain_"+task_name)
robotDim = robot.dynamic.getDimension()
first_6 = zeros((32,6))
other_dof = identity(robotDim-6)
jacobian_posture = hstack([first_6, other_dof])
taskPosture.feature.jacobianIN.value = matrixToTuple( jacobian_posture )
taskPosture.feature.setReference(taskPosture.featureDes.name)
taskPosture.add(taskPosture.feature.name)


# Create the sequence player
aPlayHppPath = PathSampler('aPlayHppPath')
aPlayHppPath.connect("ontake", 2809)
aPlayHppPath.setRootJointType("freeflyer")
aPlayHppPath.setPathID(0)
aPlayHppPath.setTimeStep(0.01)

# Connects the sequence player to the posture task
from dynamic_graph.sot.core import Selec_of_vector
from dynamic_graph import plug

# Connects the dynamics to the current feature of the posture task
getPostureValue = Selec_of_vector("current_posture")
getTargetValue  = Selec_of_vector("current_target")
getPostureValue.selec(6,robotDim)
getTargetValue .selec(6,robotDim)
plug(robot.dynamic.position, getPostureValue.sin)
plug(aPlayHppPath.configuration, getTargetValue.sin)

plug(getTargetValue.sout, taskPosture.featureDes.errorIN)
plug(getPostureValue.sout, taskPosture.feature.errorIN)
plug(robot.dynamic.position, aPlayHppPath.position)

# Set the gain of the posture task
setGain(taskPosture.gain,(4.9,0.9,0.01,0.9))
plug(taskPosture.gain.gain, taskPosture.controlGain)
plug(taskPosture.error, taskPosture.gain.error)

# Create the solver
from dynamic_graph.sot.core import SOT
sot = SOT('sot')
sot.setSize(robot.dynamic.getDimension())
plug(sot.control,robot.device.control)

taskPosture.featureDes.errorIN.recompute(0)

# Push the posture task in the solver
