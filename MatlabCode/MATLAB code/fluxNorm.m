%% Get flux normalization factor 
% Input: template(PSF), flux threshold value(Fth),
% background expectancy value(B)

% Output: flux nomrlization factor(Sf)

function Sf = fluxNorm(PSF,Fth,B)

Sf = 0;

 for j = 1:size(PSF,1)
        for k = 1: size(PSF,2)
            for t = 1:size(PSF,3)
            Sf = Sf + PSF(j,k,t)*log(1 + Fth*PSF(j,k,t)/B);
            end
        end
 end
end