%% Get initial guess for flux
% Input: background expectancy(B), false alarm probability(beta),
% template width(sigma)

% Output: initial flux guess(Fi)

function Fi = initialFlux(B,beta,sigma)

Flux = linspace(0,100,1000);
l = 4*pi*sigma^2*B;
flag = 0;

for F = Flux
    eqn = abs((1 - beta) - poisscdf(F,l));
    
    if (eqn <= 0.01)
        Fi = F;
        flag = 1;
        break;
    end
end

if (flag == 0)
    disp('Failed to find initial flux\n')
end

end