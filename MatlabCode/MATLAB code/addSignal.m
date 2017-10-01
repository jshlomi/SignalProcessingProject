%% Add signal to image
% Input: image(M), signal template(PSF), flux value(F),
% position vector(x,y,t) to place the signal in the image(pos)

% Output: image containing a signal(IMG)

function IMG = addSignal(M,PSF,F,pos)

    for i = 1:size(PSF,1)
        for j = 1:size(PSF,2)
          for t = 1:size(PSF,3)
              M(i + pos(1) - size(PSF,1)/2,j + pos(2) - size(PSF,2)/2,t + pos(3) - size(PSF,3)/2) = ...
              M(i + pos(1) - size(PSF,1)/2,j + pos(2) - size(PSF,2)/2,t + pos(3) - size(PSF,3)/2) +...
              poissrnd(F*PSF(i,j,t)); 
          end
        end
    end
    
    IMG = M;
end