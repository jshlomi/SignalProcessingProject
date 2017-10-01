%% Run a series of itterations to find the optimal threshold values
% NOTE: Poisson matched filter case 

% Input: image spacial size(size_xy), image time dim. size(size_t),
% false alaram probability(beta), background expectancy(B),
% template width(sigma), template(PSF)

% Output: flux threshold(Fth), S threshold(Sth)

function [Fth,Sth]= getThresholdsPoisson(size_xy,size_t,beta,B,sigma,PSF)

Fth = initialFlux(B,beta,sigma); % first guess for flux threshold
B_sim = B;
flag = 0;
itt = 0;
% maxitt = 10; % OPTION: limit number of itterations

while (flag == 0)
    
    itt = itt + 1;
    fprintf('iteration: %d\n',itt);
    fprintf('Fth: %.4f\n',Fth);
   
    % Generate Poisson random image with no BG subtraction
    M_sim = makeImg(B_sim,size_xy,size_t,1);
    
    % Filter image
    Filter_sim = log(1 + (Fth/B_sim)*PSF);
    Ssim = imfilter(M_sim,Filter_sim);
    
    % Determine Sth 
    Sth = prctile(Ssim(:),(1 - beta)*100);
    fprintf('Sth: %.4f\n',Sth);
    
    % Calculate Sf
    Sf = fluxNorm(PSF,Fth,B_sim);
    fprintf('Sf: %.4f\n\n',Sf);
    
    % Set new value for flux threshold
    Fth_f = (Sth/Sf) + B_sim;
    
    % Check convergence
    if (abs(Fth_f - Fth) < 0.01*Fth)
        flag = 1; % converged
    else
        Fth = Fth_f;
    end
    
    % OPTION: limit number of itterations
%     if(itt == maxitt)
%         disp('EXCEEDING MAXIMUM ITERATIONS')
%         fprintf('\n')
%         break;
%     end        
end

fprintf('Summary\n');
fprintf('Initial Fth: %.4f\n',initialFlux(B,beta,sigma));
fprintf('Final Fth: %.4f\n', Fth);
fprintf('Sth: %.4f\n', Sth);

end