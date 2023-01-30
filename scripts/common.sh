#!/bin/bash

set +e
set -o noglob

#
# Set Colors
#

bold=$(tput bold)
underline=$(tput sgr 0 1)
reset=$(tput sgr0)

red=$(tput setaf 1)
green=$(tput setaf 76)
white=$(tput setaf 7)
tan=$(tput setaf 202)
blue=$(tput setaf 25)

#
# Headers and Logging
#

underline() { printf "${underline}${bold}%s${reset}\n" "$@"
}
h1() { printf "\n${underline}${bold}${blue}%s${reset}\n" "$@"
}
h2() { printf "\n${underline}${bold}${white}%s${reset}\n" "$@"
}
debug() { printf "${white}%s${reset}\n" "$@"
}
info() { printf "${white}➜ %s${reset}\n" "$@"
}
success() { printf "${green}✔ %s${reset}\n" "$@"
}
error() { printf "${red}✖ %s${reset}\n" "$@"
}
warn() { printf "${tan}➜ %s${reset}\n" "$@"
}
bold() { printf "${bold}%s${reset}\n" "$@"
}
note() { printf "\n${underline}${bold}${blue}Note:${reset} ${blue}%s${reset}\n" "$@"
}

set -e


function check_docker {
        if ! docker --version &> /dev/null
        then
                error "Need to install docker(20.10.9+) first and run this script again."
                exit 1
        fi

        # docker has been installed and check its version
        if [[ $(docker --version) =~ (([0-9]+)\.([0-9]+)([\.0-9]*)) ]]
        then
                docker_version=${BASH_REMATCH[1]}
                docker_version_part1=${BASH_REMATCH[2]}
                docker_version_part2=${BASH_REMATCH[3]}

                note "docker version: $docker_version"
                # the version of docker does not meet the requirement
                if [ "$docker_version_part1" -lt 20 ] || ([ "$docker_version_part1" -eq 10 ] && [ "$docker_version_part2" -lt 9 ])
                then
                        error "Need to upgrade docker package to 20.10.9+."
                        exit 1
                fi
        else
                error "Failed to parse docker version."
                exit 1
        fi
}

function check_dockercompose {
        if ! docker compose version &> /dev/null
        then
                error "Need to install docker-compose(2.10.1+) by yourself first and run this script again."
                exit 1
        fi

        # docker-compose has been installed, check its version
        if [[ $(docker compose version) =~ (([0-9]+)\.([0-9]+)([\.0-9]*)) ]]
        then
                docker_compose_version=${BASH_REMATCH[1]}
                docker_compose_version_part1=${BASH_REMATCH[2]}
                docker_compose_version_part2=${BASH_REMATCH[3]}

                note "docker-compose version: $docker_compose_version"
                # the version of docker-compose does not meet the requirement
                if [ "$docker_compose_version_part1" -lt 2 ] || ([ "$docker_compose_version_part1" -lt 10 ] && [ "$docker_compose_version_part2" -lt 1 ])
                then
                        error "Need to upgrade docker-compose package to 2.10.1+."
                        exit 1
                fi
        else
                if ! [[ $(docker compose version) =~ (([0-9]+)\.([0-9]+)([\.0-9]*)) ]]
                then
                        error "Failed to parse docker-compose version."
                        exit 1
                fi
        fi
}