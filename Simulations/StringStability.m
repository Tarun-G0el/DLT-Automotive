% close all
% Gcl = tf([4 4],[1 3]);
% step(Gcl)

figure
for i=0.1:0.1:1
    hold on
    Gcl = tf([1], [1 2*i 1]);
    step(Gcl)
end