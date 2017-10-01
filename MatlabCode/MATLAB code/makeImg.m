%% Make 3D poisson random image with/without background subtraction
% Input: background expectancy(Lambda), image spacial size(size_xy),
% image time dim. size(size_t)
% OPTION - background subtraction: 
% Pass sub_BG = 1 for background subtraction
% Pass sub_BG = 0 for no subtraction

% Output: 3D poisson random image(image)

function image = makeImg(Lambda,size_xy,size_t,sub_BG)

    image = poissrnd(Lambda,size_xy,size_xy,size_t);

    if (sub_BG == 1)
        B = mean(image(:)); % [counts/pix]
        image = image - B;
    end
    
end