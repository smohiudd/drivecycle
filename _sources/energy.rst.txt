Energy Model
=========================

.. sectnum::

The battery module is used to simulate battery power requirements and battery
state of charger for a battery electric bus. It is determined using the following 
steps.

Total Tractive Force
---------------------


Rolling Resistance Force
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   F_r = \mu m g
   
* :math:`\mu`, is the coefficient of rolling resisance
* :math:`m`, mass of the vehicle in :math:`kg`
* :math:`g`, is the gravitational acceleration constant

Aerodynamic Drag Force
~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   F_{ad} = \frac{1}{2}\ \rho A C_d v^2

* :math:`\rho`, density of air
* :math:`A`, frontal area in :math:`m^2`
* :math:`C_d`, drag coefficient
* :math:`v`, velocity in :math:`m/s`


Hill Climbing Force
~~~~~~~~~~~~~~~~~~~~

.. math::

   F_h = m g sin(\alpha)

* :math:`\alpha`, grade of the slope

Acceleration Force
~~~~~~~~~~~~~~~~~~~

.. math::

   F_a = m a

* :math:`a`, acceleration of the vehicle in :math:`m/s^2`


Total Tractive Force
~~~~~~~~~~~~~~~~~~~~

.. math::

   F_t = F_r + F_{ad} + F_h + F_a


Energy to move the Vehicle
---------------------------

.. math::

   P_t = F_t v

Energy Model
------------

Depending on if the vehicle is accelerating or decelerating power may be supplied to or extracted from the the battery. 

Considering the following component efficiencies:

* :math:`\eta_m`, motor efficiency
* :math:`\eta_t`, transmission efficiency
* :math:`\eta_c`, power converter efficiency

We can determine the power going into or out of the battery using the following equations:


Torque at the wheel,

.. math::

   T_w = F_t \times r_w


Torque at the motor,

.. math::

   T_m = {\dfrac{T_w}{Gear Ratio \times \eta_T}}


Rotational speed of the wheels,


.. math::

   \omega_w = {\dfrac{v}{r_w}}


Rotational speed of the motor,

.. math::

   \omega_m = {\dfrac{\omega_w}{Gear Ratio}}


Finally, the instatneous power supplied by the battery is,

.. math::

   P = {\dfrac{T_m \times \omega_m}{\eta_m \times \eta_c}}


When the vehicle is decelerating, a propotion of he braking force may be used for regeneration. 

.. math::

      F_{reg} = RegenRatio \times F_t


And the power supplied to the battery can be determined as follow:

.. math::

      T_{reg} = F_{reg} \times r_w


      P = {\dfrac{T_{reg} \times \omega_m}{\eta_m \times \eta_c}}


References
-----------

1. Franca, A. (2015). Electricity consumption and battery lifespan estimation for transit electric buses: drivetrain simulation and electrochemical modelling. Masters Thesis. University of Victoria. 
2. Larmine, J., Lowry J. (2012). Electric Vehicle Technology Explained Second Edition. Wiley.






