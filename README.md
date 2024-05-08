Python Robotics Simulator
================================

This is a simple, portable robot simulator developed by [Student Robotics](https://studentrobotics.org).
Some of the arenas and the exercises have been modified for the Research Track I course (Robotics Engineering, UniGE)

Assignment
---------

The goal of the assignment is to make the robot:
- constrantly drive the robot around the circuit in the counter-clockwise direction
- avoid touching the golden boxes
- when the robot is close to a silver box, it should grab it, and move it behind itself

The code of the assignment is `assignment.py`, so to run the code simply move to the folder `python_simulator/robot-sim/` and run the following line:

```bash
$ python run.py assignment.py
```
That's the pseudocode of the code developed:

### ###
```
loop :

  if there is a golden boxes near in front :
    turn until there is not

  if there is a silver box near in front :
    go take it and put it behind

  move forward
```

To put into code this, 5 functions has been written.

First if functions:
  - `control_gold()` --- **called by main** ---   check if there are golden boxes near.
    If yes, the robot (recursively) turn right/left until there is no risk to hit them.
    First if checks if the golden box is at a critical `|angle|<30`, so that we call `choose_direction` function to decide at which direction is better to turn, by checking the number of side's boxes.
    - `choose_direction()` --- **called by control_gold and by put_silver_behind** --- choose the better direction to turn(right/left).
    We count the golden box at the right and at the left, choosing the direction where
    there are less.
    The counting is weighted propoctionally to the distance(more near = more weight). It returns `True` if there are more boxes at right, `False` if there are more at left.


Second if functions:
  - `control_silver()` --- **called by main** --- checks if there is a silver box near in front. If yes, the robot aligns to it and goes to put it behind.
    - `align_with_silver()` --- **called by control_silver** ---   aligns with the silver box.
    If it's well aligned it returns, otherwise he turn left/right (recursively check if
    until it's well aligned).
    - `put_silver_behind()` --- **called by control_silver** ---  put the (aligned) silver box behind.
    If it's close enough, he grabs it and releases it behind, turning in the side where there are less boxes (by calling `choose_direction`)
    else he get closer (recursively check if it's close enough).


With those function, the actual main code becomes simpler than the pseudocode itself:

```
while 1:
    control_gold()				  
    control_silver()
    drive(100,0.1)
```


I think the code can be improved by creating a function to turn a specific angle given in input, so that we can have a better control of the robot.
But this cannot be done because the behaviour could change a little bit at every launch.
Also, we could improve `choose_direction` function by making some more experiments and find worst cases, so that we modify the function to get through those cases.



Installing and running
----------------------

The simulator requires a Python 2.7 installation, the [pygame](http://pygame.org/) library, [PyPyBox2D](https://pypi.python.org/pypi/pypybox2d/2.1-r331), and [PyYAML](https://pypi.python.org/pypi/PyYAML/).

To run one or more scripts in the simulator, use `run.py`, passing it the file names. 


## Troubleshooting

Pygame, unfortunately, can be tricky (though [not impossible](http://askubuntu.com/q/312767)) to install in virtual environments. If you are using `pip`, you might try `pip install hg+https://bitbucket.org/pygame/pygame`, or you could use your operating system's package manager. Windows users could use [Portable Python](http://portablepython.com/). PyPyBox2D and PyYAML are more forgiving, and should install just fine using `pip` or `easy_install`.


When running `python run.py <file>`, you may be presented with an error: `ImportError: No module named 'robot'`. This may be due to a conflict between sr.tools and sr.robot. To resolve, symlink simulator/sr/robot to the location of sr.tools.

On Ubuntu, this can be accomplished by:
* Find the location of srtools: `pip show sr.tools`
* Get the location. In my case this was `/usr/local/lib/python2.7/dist-packages`
* Create symlink: `ln -s path/to/simulator/sr/robot /usr/local/lib/python2.7/dist-packages/sr/`


Robot API
---------

The API for controlling a simulated robot is designed to be as similar as possible to the [SR API][sr-api].

### Motors ###

The simulated robot has two motors configured for skid steering, connected to a two-output [Motor Board](https://studentrobotics.org/docs/kit/motor_board). The left motor is connected to output `0` and the right motor to output `1`.

The Motor Board API is identical to [that of the SR API](https://studentrobotics.org/docs/programming/sr/motors/), except that motor boards cannot be addressed by serial number. So, to turn on the spot at one quarter of full power, one might write the following:

```python
R.motors[0].m0.power = 25
R.motors[0].m1.power = -25
```

### The Grabber ###

The robot is equipped with a grabber, capable of picking up a token which is in front of the robot and within 0.4 metres of the robot's centre. To pick up a token, call the `R.grab` method:

```python
success = R.grab()
```

The `R.grab` function returns `True` if a token was successfully picked up, or `False` otherwise. If the robot is already holding a token, it will throw an `AlreadyHoldingSomethingException`.

To drop the token, call the `R.release` method.

Cable-tie flails are not implemented.

### Vision ###

To help the robot find tokens and navigate, each token has markers stuck to it, as does each wall. The `R.see` method returns a list of all the markers the robot can see, as `Marker` objects. The robot can see all the markers which it is facing towards.

Each `Marker` object has the following attributes:

* `info`: a `MarkerInfo` object describing the marker itself. Has the following attributes:
  * `code`: the numeric code of the marker.
  * `marker_type`: the type of object the marker is attached to (either `MARKER_TOKEN_GOLD`, `MARKER_TOKEN_SILVER` or `MARKER_ARENA`).
  * `offset`: offset of the numeric code of the marker from the lowest numbered marker of its type. For example, token number 3 has the code 43, but offset 3.
  * `size`: the size that the marker would be in the real game, for compatibility with the SR API.
* `centre`: the location of the marker in polar coordinates, as a `PolarCoord` object. Has the following attributes:
  * `length`: the distance from the centre of the robot to the object (in metres).
  * `rot_y`: rotation about the Y axis in degrees.
* `dist`: an alias for `centre.length`
* `res`: the value of the `res` parameter of `R.see`, for compatibility with the SR API.
* `rot_y`: an alias for `centre.rot_y`
* `timestamp`: the time at which the marker was seen (when `R.see` was called).

For example, the following code lists all of the markers the robot can see:

```python
markers = R.see()
print "I can see", len(markers), "markers:"

for m in markers:
    if m.info.marker_type in (MARKER_TOKEN_GOLD, MARKER_TOKEN_SILVER):
        print " - Token {0} is {1} metres away".format( m.info.offset, m.dist )
    elif m.info.marker_type == MARKER_ARENA:
        print " - Arena marker {0} is {1} metres away".format( m.info.offset, m.dist )
```

[sr-api]: https://studentrobotics.org/docs/programming/sr/
