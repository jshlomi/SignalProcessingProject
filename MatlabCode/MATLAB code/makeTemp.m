%% Make 3D PSF (Gaussian in XY, decaying exponent in t)
% Input: image spacial size(size_xy), image time dim. size(size_t),
% template width(sigma), flare decay rate(Decay_rate),
% flare time range(t_range)

% Output: 3D PSF(PSF), Flare profile in time(FlareModel)

function [PSF,FlareModel] = makeTemp(size_xy,size_t,sigma,Decay_rate,t_range)

PSF_nn = zeros(size_xy,size_xy,size_t);
mu = [size_xy/2 size_xy/2]; % 2D Gaussian mean values
Time_p = zeros(length(size_t),1);

for t = t_range
    Time_p(t) = exp(-Decay_rate*t);
    for i = 1:size_xy
        for j = 1:size_xy
            PSF_nn(i,j,t) = (Time_p(t)/(2*pi*sigma^2))*exp(-((i - mu(1))^2 + (j - mu(2))^2)/(2*sigma^2));
        end
    end
end

PSF = (1/sum(PSF_nn(:)))* PSF_nn; % Normalization
FlareModel = Time_p;
end