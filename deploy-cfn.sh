#!/bin/bash

set +x -eEu -o pipefail

PARAMS=""
SHORT_AWS_PROFILE=""
LONG_AWS_PROFILE=""
CFN_CONFIG=""
SCEPTRE_PROJECT=""
DRY_RUN=""

get_short_term_credentials() {
    unset AWS_ACCESS_KEY AWS_SECRET_KEY AWS_SECURITY_TOKEN AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
    AWS_ACCESS_KEY=$(grep -A6 "\[${SHORT_AWS_PROFILE}\]" ~/.aws/credentials | grep aws_access_key_id | awk '{print $NF}')
    AWS_SECRET_KEY=$(grep -A6 "\[${SHORT_AWS_PROFILE}\]" ~/.aws/credentials | grep aws_secret_access_key | awk '{print $NF}')
    AWS_SECURITY_TOKEN=$(grep -A6 "\[${SHORT_AWS_PROFILE}\]" ~/.aws/credentials | grep aws_session_token | awk '{print $NF}')
    AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY
    AWS_SECRET_ACCESS_KEY=$AWS_SECRET_KEY
    AWS_SESSION_TOKEN=$AWS_SECURITY_TOKEN
    export AWS_ACCESS_KEY AWS_SECRET_KEY AWS_SECURITY_TOKEN AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
}

get_long_term_credentials() {
    unset AWS_ACCESS_KEY AWS_SECRET_KEY AWS_SECURITY_TOKEN AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
    AWS_ACCESS_KEY=$(grep -A2 "\[${LONG_AWS_PROFILE}\]" ~/.aws/credentials | grep aws_access_key_id | awk '{print $NF}')
    AWS_SECRET_KEY=$(grep -A2 "\[${LONG_AWS_PROFILE}\]" ~/.aws/credentials | grep aws_secret_access_key | awk '{print $NF}')
    AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY
    AWS_SECRET_ACCESS_KEY=$AWS_SECRET_KEY
    export AWS_ACCESS_KEY AWS_SECRET_KEY AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY
}


launch() {
    local SCRIPT_ACTION=$1
    local CFN_CONFIG=$2

    local STACK_NAME=$(echo ${CFN_CONFIG} | cut -d'.' -f1)
    local SOURCE_REPO_URL=$(git remote get-url origin | cut -d':' -f2)
    local BASE_DIR=$(pwd)
    echo "Entering ${SCEPTRE_PROJECT}/"
    cd "${SCEPTRE_PROJECT}"

    local STACK_STATUS=$(sceptre \
        "${ARG_ARRAY[@]}" \
        status ${CFN_CONFIG} | jq -r ".\"${STACK_NAME}\"")

    if [ "z${SCRIPT_ACTION}" == "zdeploy" ]; then
        # If it's in ROLLBACK_COMPLETE state, delete the current stack
        if [ "z${STACK_STATUS}" == "zROLLBACK_COMPLETE" ]; then
            if [ "z${DRY_RUN}" == "z" -o "z${DRY_RUN}" == "zfalse" ]; then
                sceptre \
                    "${ARG_ARRAY[@]}" \
                    delete -y ${CFN_CONFIG}
            fi
            ACTION="create -y"

        elif [ "z${STACK_STATUS}" == "zCREATE_COMPLETE" -o "z${STACK_STATUS}" == "zUPDATE_COMPLETE" -o "z${STACK_STATUS}" == "zUPDATE_ROLLBACK_COMPLETE" ]; then
          ACTION="update -y"
        else
          ACTION="create -y"
        fi
    elif [ "z${SCRIPT_ACTION}" == "zdestroy" ]; then
        ACTION="delete -y"
    elif [ "z${SCRIPT_ACTION}" == "zgenerate" ]; then
        ACTION="generate"
    else
      echo "Invalid action. You need to define action as"
      echo "$0 -n <action>"
      echo "Where valid actions are choice of deploy, destroy, generate"
    fi

    if [ "z${DRY_RUN}" == "z" -o "z${DRY_RUN}" == "zfalse" ]; then
        echo "[Calling:]"
        echo "sceptre \
          "${ARG_ARRAY[@]}" \
          ${ACTION} ${CFN_CONFIG}"
        sceptre \
          "${ARG_ARRAY[@]}" \
          ${ACTION} ${CFN_CONFIG}
    fi
    local EXIT_STATUS="$?"
    cd "${BASE_DIR}"
    exit $?
}

parse_arguments() {
    while (( "$#" )); do
      case "$1" in
        -l|--long-term-profile)
          LONG_AWS_PROFILE=$2
          shift 2
          ;;
        -s|--short-term-profile)
          SHORT_AWS_PROFILE=$2
          # SWITCH_ACCOUNT=0
          shift 2
          ;;
        -e|--extra-vars)
          ARG_ARRAY+=("--var" "${2}")
          shift 2
          ;;
        -f|--var-file)
          ARG_ARRAY+=("--var-file" "./vars/${2}")
          shift 2
          ;;
        -n|--action)
          SCRIPT_ACTION=$2
          shift 2
          ;;
        -p|--project)
          SCEPTRE_PROJECT=$2
          shift 2
          ;;
        -i|--item)
          CFN_CONFIG=$2
          shift 2
          ;;
        -d|--dry-run)
          DRY_RUN=$2
          shift 2
          ;;
        --) # end argument parsing
          shift
          break
          ;;
        -*|--*=) # unsupported flags
          echo "Error: Unsupported flag $1" >&2
          exit 1
          ;;
        *) # preserve positional arguments
          PARAMS="$PARAMS $1"
          shift
          ;;
      esac
    done
    # set positional arguments in their proper place
    eval set -- "$PARAMS"
}

get_template() {
    local branch=main
    git clone -b "${branch}" --depth 1 https://github.com/harisfauzi/shared-sceptre-template.git shared-sceptre-template
    local CURRENT_DIR=$(pwd)
    (cd "${CURRENT_DIR}/shared-sceptre-template/templates"; tar cf - .) | (cd "${CURRENT_DIR}/${SCEPTRE_PROJECT}/templates"; tar xf -)
    rm -rf shared-sceptre-template
}

start_python_env() {
    virtualenv .venv -p /usr/bin/python3
    source .venv/bin/activate
    pip install jinja2-cli
    pip install yml2json
    pip install sceptre==2.6.2
    pip install awscli
}

end_python_env() {
    deactivate
}

main() {
    # SWITCH_ACCOUNT=1
    parse_arguments "$@"

    start_python_env

    if [ "z$SHORT_AWS_PROFILE" != "z" ]; then
        get_short_term_credentials
    elif [ "z$LONG_AWS_PROFILE" != "z" ]; then
        get_long_term_credentials
    fi

    get_template
    launch "${SCRIPT_ACTION}" "${CFN_CONFIG}"
    end_python_env
}

main "$@"
