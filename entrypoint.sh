#!/bin/bash


PLUGIN_ARGS=

if [ -n "${MATTERMOST_USERNAME}" ]; then
	PLUGIN_ARGS="${PLUGIN_ARGS} --username ${MATTERMOST_USERNAME}"
fi

if [ -n "${MATTERMOST_CHANNEL}" ]; then
	PLUGIN_ARGS="${PLUGIN_ARGS} --channel ${MATTERMOST_CHANNEL}"
fi

if [ -n "${MATTERMOST_ICON}" ]; then
	PLUGIN_ARGS="${PLUGIN_ARGS} --icon ${MATTERMOST_ICON}"
fi


EVENTS=( PUSH TAG )
for POSSIBLE_EVENT in "${EVENTS[@]}"; do
	ENV_NAME="MATTERMOST_EVENT_${POSSIBLE_EVENT}"
	eval VALUE=\$${ENV_NAME}
	if [ -n "${VALUE}" ]; then
		if [ "${VALUE}" == "1" -o "${VALUE}" == "yes" -o "${VALUE}" == "y" ]; then
			PLUGIN_ARGS="${PLUGIN_ARGS} --${POSSIBLE_EVENT,,}"
		fi
	fi
done

NEGATIVE_EVENTS=( ISSUE COMMENT MERGE-REQUEST CI )
for POSSIBLE_EVENT in "${NEGATIVE_EVENTS[@]}"; do
	ENV_NAME="MATTERMOST_EVENT_${POSSIBLE_EVENT}"
	eval VALUE=\$${ENV_NAME}
	if [ -n "${VALUE}" ]; then
		if [ "${VALUE}" == "0" -o "${VALUE}" == "n" -o "${VALUE}" == "no" ]; then
			PLUGIN_ARGS="${PLUGIN_ARGS} --no-${POSSIBLE_EVENT,,}"
		fi
	fi
done

if [ ! -x "/usr/local/bin/mattermost_gitlab" ]; then
	echo "Missing application executable !" >&2
	exit 1
fi

echo "Starting: "
echo "/usr/local/bin/mattermost_gitlab ${PLUGIN_ARGS}"
/usr/local/bin/mattermost_gitlab ${PLUGIN_ARGS}
