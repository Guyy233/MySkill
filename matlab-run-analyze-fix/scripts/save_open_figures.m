function save_open_figures(outputDir)
% Save all open MATLAB figures as PNG files.

    if nargin < 1 || strlength(string(outputDir)) == 0
        outputDir = fullfile(pwd, 'output', 'matlab-runs', datestr(now, 'yyyymmdd_HHMMSS'));
    end

    if ~exist(outputDir, 'dir')
        mkdir(outputDir);
    end

    figs = findall(0, 'Type', 'figure');
    figs = flipud(figs);

    for idx = 1:numel(figs)
        fig = figs(idx);
        fileBase = sprintf('figure_%02d', idx);
        pngPath = fullfile(outputDir, [fileBase '.png']);
        exportgraphics(fig, pngPath, 'Resolution', 150);
    end
end
