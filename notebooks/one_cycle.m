% ******************************
% ONE CYCLE
% This script file performs one cycle, of any
% drive cycle of N points with any vehicle and
% for lead acid or NiCad batteries.
% All the appropriate variables must be set
% by the calling program.
% *******************************
for C=2:N
    accel=V(C) - V(C-1);
    Fad = 0.5 * 1.25 * area * Cd * V(C)^2; % Equation (8.2)
    Fhc = 0; % Equation (8.3), assume flat
    Fla = 1.05 * mass * accel;% The mass is increased modestly to compensate for
    % the fact that we have excluded the moment of inertia
    
    Pte = (Frr + Fad + Fhc + Fla)*V(C); %Equations (8.9) & (8.23)**
    
    omega = Gratio * V(C);
    if omega == 0 % Stationary
        Pte=0;
        Pmot_in=0; % No power into motor
        Torque=0;
        eff_mot=0.5; % Dummy value, to make sure not zero.
    elseif omega > 0 % Moving
        if Pte < 0
            Pte = Regen ratio * Pte; % Reduce the power if
        end; % braking, as not all will be by the motor.
        % We now calculate the output power of the motor,
        % which is different from that at the wheels, because
        % of transmission losses.
        if Pte>=0
            Pmot_out=Pte/G eff; % Motor power > shaft power
        elseif Pte<0
            Pmot_out=Pte * G eff; % Motor power diminished
        end; % if engine braking.
        
        Torque=Pmot_out/omega; % Basic equation, P=T*omega
        
        if Torque>0 % Now use Equation (8.23)**
            eff_mot=(Torque*omega)/((Torque*omega)+((Torque^2)*kc)+(omega*ki)+((omega^3)*kw)+ConL);
        elseif Torque<0
            eff_mot=(-Torque*omega)/((-Torque*omega) + ((Torque^2)*kc)+(omega*ki)+((omega^3)*kw)+ConL);
        end;
        
        if Pmot out > = 0
            Pmot_in = Pmot out/eff mot; % Equation (8.23)**
        elseif Pmot out < 0
            Pmot_in = Pmot out * eff mot;
        end;
    end;
    
    Pbat = Pmot_in + Pac; % Equation (8.26)**

    if bat_type=='NC'
        E=open circuit_voltage_NC(DoD(C-1),NoCells);
    elseif bat_type=='LA'
        E=open circuit_voltage_LA(DoD(C-1),NoCells);
    else
        error('Invalid battery type');
    end;

    if Pbat > 0 % Use Equation (3.26)**
        I = (E - ((E*E) - (4*Rin*Pbat))^0.5)/(2*Rin);
        CR(C) = CR(C-1) +((I^k)/3600); %Equation (3.24)**
    elseif Pbat==0
        I=0;
    elseif Pbat <0
    % Regenerative braking. Use Equation (3.28)**, and
    % double the internal resistance.
        Pbat = - 1 * Pbat;
        I = (-E + (E*E + (4*2*Rin*Pbat))^0.5)/(2*2*Rin);
        CR(C) = CR(C-1) - (I/3600); %Equation (3.29)**
    end;
    
    DoD(C) = CR(C)/PeuCap; %Equation (2.19)**
    
    if DoD(C)>1
        DoD(C) =1;
    end
    % Since we are taking 1 second time intervals,
    % the distance travelled in metres is the same
    % as the velocity. Divide by 1000 for km.
    D(C) = D(C-1) + (V(C)/1000);
    XDATA(C)=C; % See Section 8.4.4 for the use
    YDATA(C)=eff mot; % of these two arrays.

    end;
    % Now return to calling program.
    
