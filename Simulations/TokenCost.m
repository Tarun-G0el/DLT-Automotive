clc
clear all
close all

%%
% Time in seconds in one day: 86400
day = 86400;
% Ts = 10: Time taken for signal to allow vehicles to pass, so wasted time
Ts = 10;
day_left = day / Ts;
% Fj = 3: Number of Vehicles that pass during allowed time
Fj = 3;
% Tj = 1: Time taken for vehicles to pass
Tj = 1;
num_veh_pass = day_left / (Fj * Tj);

%%
a = 1;
b = num_veh_pass;
r = (b-a).*rand(floor(0.01*num_veh_pass),1) + a;
r = floor(r(:));


%%
Ct = 0;
Qt = 0;
size = num_veh_pass;
z = zeros(1, size);
y = zeros(1, size);
x = zeros(1, size);
for i=1:size
    Ct1 = Ct + (0.1)*(1-Qt);
    Ct = Ct1;
    z(i) = Qt;
    y(i) = Ct1;
    x(i) = i;
    Qt = Ct*0.6;
end

plot(x,y)
title('Cost funtion in Units of DLT Tokens')
xlabel('Activity Number')
ylabel('C(t)')
figure
plot(x,z)
title('Compliance Levels in Range [0 - 1]')
axis([0 3000 0 1.8])
xlabel('Activity Number')
ylabel('Q(t)')