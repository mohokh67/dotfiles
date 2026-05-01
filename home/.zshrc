# PATH exports (set early before tool initialization)
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$HOME/.npm-global/bin:$PATH"
export EDITOR="zed"

# Oh My Zsh configuration
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME=""  # Disabled - using oh-my-posh instead
zstyle ':omz:update' mode auto

plugins=(direnv)

source $ZSH/oh-my-zsh.sh

# NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# Tool initializations
if [ "$TERM_PROGRAM" != "Apple_Terminal" ]; then
    eval "$(oh-my-posh init zsh --config $HOME/.oh-my-posh.toml)"
fi

. "$HOME/.local/bin/env"

eval "$(atuin init zsh)"

eval $(thefuck --alias)
# You can use whatever you want as an alias, like for Mondays:
eval $(thefuck --alias FUCK)

############################################ Functions
lsofport() {
  if [ -z "$1" ]; then
    echo "Usage: lsofport <port>"
  else
    lsof -i :$1
  fi
}

mkcd() {
  mkdir -p "$1" && cd "$1"
}

# press CRTL + T and then check the preview with bat
# If this command does not work, run this: "$(brew --prefix)/opt/fzf/install"
eval "$(fzf --zsh)"
export FZF_CTRL_T_OPTS="--preview 'bat --color=always --style=numbers --line-range=:500 {}'"
# [ -f ~/.fzf.zsh ] && source ~/.fzf.zsh



function y() {
	local tmp="$(mktemp -t "yazi-cwd.XXXXXX")" cwd
	command yazi "$@" --cwd-file="$tmp"
	IFS= read -r -d '' cwd < "$tmp"
	[ "$cwd" != "$PWD" ] && [ -d "$cwd" ] && builtin cd -- "$cwd"
	rm -f -- "$tmp"
}

########################################### caeapace
autoload -U compinit && compinit
# export CARAPACE_BRIDGES='zsh,fish,bash,inshellisense' # optional
# zstyle ':completion:*' format $'\e[2;37mCompleting %d\e[m'
zstyle ':completion:*:git:*' group-order 'main commands' 'alias commands' 'external commands' menu select
source <(carapace _carapace)

############################################ Aliases

alias zshconfig="zed ~/.zshrc -e"
alias reload='source ~/.zshrc;echo "ZSH aliases sourced."'
alias edit="zed . --classic"
alias view="zed . --classic"

alias c='clear'

# Replace OS commands: Begin
alias cat='bat'
alias find='fd'

# install this with brew: cbonsai
alias screensaver="cbonsai -S"

# alias ls='ls --color=auto'
alias ls="eza --long --git --icons --group-directories-first"
alias ll="eza -la --git --icons --group-directories-first"
alias lst="eza -l -T --git --icons --group-directories-first"
alias lsta="eza -la -T --git --icons --group-directories-first"

# Replace OS commands: End

alias cd..='cd ..'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias -- -='cd -'
cx(){
    cd "$1" && ll
}

alias h='history'
alias home='cd ~'

alias path='echo -e ${PATH//:/\\n}'
alias now='date +"%T"'
alias nowdate='date +"%d-%m-%Y"'

# brew install ghostscript
# this needs to be before gs(git status) alias for no confusion
pdfcompress() {
  local input="$1"
  local output="${input%.pdf}_output.pdf"

  command gs -sDEVICE=pdfwrite \
    -dCompatibilityLevel=1.4 \
    -dNOPAUSE -dQUIET -dBATCH \
    -dDownsampleColorImages=true \
    -dColorImageDownsampleType=/Bicubic \
    -dColorImageResolution=120 \
    -dJPEGQ=75 \
    -sOutputFile="$output" \
    "$input"

    echo "$output created."
}

# Git
alias gs='git status'
alias ga='git add'
alias gaa='git add --all'
alias gb='git branch'
alias gco='git checkout'
alias gcb='git checkout -b'
alias gd='git diff'
alias gds='git diff --staged'
alias gl='git log --oneline -20'
alias gpull='git pull'
alias gpush='git push'
alias gmain='git checkout main'
alias gcommit='git commit -m'
alias gst='git stash'
alias gstp='git stash pop'
alias gundo='git reset HEAD~1 --soft'

# Github CLI
alias ghw="gh repo view --web"
alias ghpr="gh pr create"
alias ghprs="gh pr list"
alias ghprv="gh pr view"
alias ghprc="gh pr checkout"
alias ghprm="gh pr merge"
alias ghpr-web="gh pr view --web"
alias ghi="gh issue list"
alias ghic="gh issue create"
alias ghiv="gh issue view"
alias ghi-web="gh issue view --web"
alias ghrc="gh repo clone"
alias ghrf="gh repo fork"
alias ghr="gh run list"
alias ghrw="gh run watch"

# AWS
alias awsconfig='zed ~/.aws/config --classic'
alias aws-sso='aws --profile sso sso login'

# Docker
alias docker-stop-all='docker stop $(docker ps -q)'
alias dps='docker ps'
alias dpsa='docker ps -a'
alias dimg='docker images'
alias drm='docker rm $(docker ps -aq)'
alias drmi='docker rmi'
alias dlog='docker logs -f'
alias dex='docker exec -it'

# Nodejs
alias update-packages="npx npm-check-updates"
alias sort-package-json="npx sort-package-json"
alias npkill="npx npkill"
alias pn="pnpm"
alias nis='npm i --save'
alias nid='npm i -D'

# Python
alias python="uv run python"
alias python3="uv run python"
alias pip="uv run pip"

# Claude CLI
alias cc="claude"
alias cch="claude --model haiku"
alias ccx="claude --dangerously-skip-permissions"

# System/Utility
alias ip="curl -s ifconfig.me"
alias localip="ipconfig getifaddr en0"
alias ports="lsof -i -P -n | grep LISTEN"
alias flushdns="sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder"
alias diskusage="du -sh * | sort -hr"
alias weather="curl wttr.in"

# File operations (safe mode)
alias cp='cp -iv'
alias copy='rsync -ah --progress --ignore-errors --log-file=rsync.log'
alias mv='mv -iv'
alias move='rsync -ah --progress --ignore-errors --log-file=rsync.log --remove-source-files'
alias mkdir='mkdir -pv'

# Quick edit
alias hosts='sudo zed /etc/hosts --classic'
alias gitconfig='zed ~/.gitconfig -e'

# YouTube video downloader
# brew install ffmpeg
# brew install yt-dlp
alias youtube='noglob yt-dlp \
  -f "bestvideo+bestaudio" \
  --merge-output-format mp4 \
  --output "$HOME/Downloads/youtube/%(title)s-%(id)s.%(ext)s" \
  --embed-thumbnail \
  --add-metadata \
  --concurrent-fragments 16 \
  --ignore-errors \
  --cookies-from-browser firefox'

alias youtube-720='yt-dlp \
  -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --merge-output-format mp4 \
  --output "$HOME/Downloads/youtube/%(title)s-%(id)s.%(ext)s" \
  --embed-thumbnail \
  --add-metadata \
  --concurrent-fragments 16 \
  --ignore-errors \
  --cookies-from-browser firefox'

alias youtube-audio='yt-dlp \
  -f "bestaudio[ext=m4a]/bestaudio" \
  --output "$HOME/Downloads/youtube/%(title)s-%(id)s.%(ext)s" \
  --embed-thumbnail \
  --add-metadata \
  --concurrent-fragments 16 \
  --ignore-errors \
  --cookies-from-browser firefox'

############################################ Aliases end

brewall() {
  echo "Upgrade: [1] all  [2] casks only  [3] formulae only"
  read -r "mode?Choice (default: 1): "
  mode=${mode:-1}

  local -a upgrade_cmd
  case $mode in
    2) upgrade_cmd=(brew upgrade --cask) ;;
    3) upgrade_cmd=(brew upgrade --formula) ;;
    *) upgrade_cmd=(brew upgrade) ;;
  esac

  echo "=============================="
  echo "Homebrew maintenance started: $(date)"
  echo "=============================="

  echo "\n[1/6] Updating Homebrew..."
  brew update || { echo "[FAIL] brew update failed at $(date)"; return 1; }
  echo "[OK] Homebrew updated"

  echo "\n[2/6] Upgrading..."
  $upgrade_cmd || { echo "[FAIL] upgrade failed at $(date)"; return 1; }
  echo "[OK] Upgrades completed"

  echo "\n[3/6] Cleaning old cache..."
  brew cleanup --prune=all || { echo "[FAIL] brew cleanup failed at $(date)"; return 1; }
  echo "[OK] Cleanup completed"

  echo "\n[4/6] Removing unused deps..."
  brew autoremove || { echo "[FAIL] brew autoremove failed at $(date)"; return 1; }
  echo "[OK] Autoremove completed"

  echo "\n[5/6] Syncing Brewfile..."
  brew bundle dump --force || { echo "[FAIL] brew bundle dump failed at $(date)"; return 1; }
  echo "[OK] Brewfile updated"

  echo "\n[6/6] Diagnostics..."
  brew doctor || echo "[WARN] brew doctor reported issues"

  echo "=============================="
  echo "Homebrew maintenance finished: $(date)"
  echo "=============================="
}

# Disable zoxide doctor warnings
export _ZO_DOCTOR=0

eval "$(zoxide init --cmd cd zsh)"
