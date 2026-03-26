-- Pull in the wezterm API
local wezterm = require 'wezterm'

-- This will hold the configuration.
local config = wezterm.config_builder()

-- This is where you actually apply your config choices.

-- For example, changing the initial geometry for new windows:
config.initial_cols = 120
config.initial_rows = 28

-- or, changing the font size and color scheme.
config.font_size = 15
config.line_height = 1.2

-- config.color_scheme = 'catppuccin-latte'
-- config.color_scheme = 'catppuccin-Mocha'
config.color_scheme = 'catppuccin-frappe'
-- config.color_scheme = 'catppuccin-macchiato'

config.font = wezterm.font 'JetBrainsMono Nerd Font'


config.colors = {
    cursor_bg = '#7aa2f7',
    cursor_border = '#7aa2f7'
}

-- config.window_decorations = 'RESIZE'

config.keys = {
    {
        key = 'w',
        mods = 'CMD',
        action = wezterm.action.CloseCurrentPane { confirm = false },
    },
    {
        key = 'd',
        mods = 'CMD',
        action = wezterm.action.SplitHorizontal { domain = 'CurrentPaneDomain' },
    },
    {
        key = 'd',
        mods = 'CMD|SHIFT',
        action = wezterm.action.SplitVertical { domain = 'CurrentPaneDomain' },
    },
    {
        key = 'k',
        mods = 'CMD',
        action = wezterm.action.SendString 'clear\n',
    }
}

config.window_background_opacity = 0.96
config.macos_window_background_blur = 23


-- Finally, return the configuration to wezterm:
return config
