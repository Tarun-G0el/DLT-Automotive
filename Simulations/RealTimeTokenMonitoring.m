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
a = 1;      % Range of vehicles
b = num_veh_pass;
percentage = 1; % Choose a value between 0% - 100%: eg 1 = 1% and 34 = 34%
r = (b-a).*rand(floor((percentage/100)*num_veh_pass),1) + a;    % Random vehicles break rules
r = floor(r(:));            % Make sure this is then an integer value to index later


%%
Ct = 1.6667;        
Qt = 1;
size = num_veh_pass;
% Q = randi([0 1], 1, size);
% Q = ones(1, size);
% Q(1) = 0;
% Q(5:5:num_veh_pass) = randi([0 1]);
% Q(1500:num_veh_pass) = 1;
z = zeros(1, size);
y = zeros(1, size);
x = zeros(1, size);
% limit = 0.99;
% last_compliance = 0;
for i=1:size
%     if Qt < 0.7
%         Ct1 = Ct + (0.1)*(1-Qt);
%     elseif Ct1 > 0
%         Ct1 = Ct - (0.1)*(1-Qt);
%     else
%         Ct1 = 0;
%     end
    Ct1 = Ct + (0.1)*(1-Qt);
    Ct = Ct1;
    z(i) = Qt;
    y(i) = Ct1;
    x(i) = i;
    if ~isempty(find(r==i, 1))
        Qt = 0.95;
    else
        Qt = Ct*0.6;
    end
%     Qt = mean(Q(1:i));
end

plot(x,y)
title('Cost funtion in Units of DLT Tokens')
% axis([0 3000 1.6 1.7])
xlabel('Activity Number')
ylabel('C(t)')
figure
plot(x,z)
title('Compliance Levels')
% axis([0 3000 0.9 1.1])
xlabel('Activity Number')
ylabel('Q(t)')