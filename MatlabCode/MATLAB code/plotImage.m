%% Plot 2D colormap of 3D array sliced at a specific axis and axis value
% Input: 3D array(image), slicing axis(sAxis), slicing axis value(sVal),
% plot title(tit)

% Output: 2D colormap plot

function plotImage(image,sAxis,sVal,tit)

if (sAxis == 'x')
    slice2D = squeeze(image(sVal,:,:));
    xl = 't';
    yl = 'y';
end

if (sAxis == 'y')
    slice2D = squeeze(image(:,sVal,:));
    xl = 't';
    yl = 'x';
end

if (sAxis == 't')
    slice2D = squeeze(image(:,:,sVal));
    xl = 'x';
    yl = 'y';
end

imagesc(slice2D)
title([tit ' 2D cut for ' sAxis ' = ' num2str(sVal) ' '])
colorbar
xlabel(xl)
ylabel(yl)


end

