# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific environment
if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]
then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi
export PATH

# User specific aliases and functions
if [ -d ~/.bashrc.d ]; then
	for rc in ~/.bashrc.d/*; do
		if [ -f "$rc" ]; then
			. "$rc"
		fi
	done
fi

unset rc

rs-status () {
  echo -ne "\033]0; $1 \007"
}

rs-check() {
  if [ "$1" = "file_exists" ]; then
      if [ ! -f "$2" ]; then
          echo "ERROR:  FILE $1 doesn't exist."
          exit 1
      fi
  fi
  if [ "$1" = "dir_exists" ]; then
      if [ ! -d "$2" ]; then
          echo "ERROR:  DIRECTORY $1 doesn't exist."
          exit 1
      fi
  fi
  if [ "$1" = "file_contains" ]; then
      if ! grep -q "$2" "$3"; then
          echo "ERROR:  FILE $3 doesn't contain $2."
          exit 1
      fi
  fi
  if [ "$1" = "package_exists" ]; then
      if ! rpm -q "$2"; then
          echo "ERROR:  PACKAGE $2 doesn't exist."
          exit 1
      fi
  fi
}

RSUSER=$(whoami)
export RSUSER