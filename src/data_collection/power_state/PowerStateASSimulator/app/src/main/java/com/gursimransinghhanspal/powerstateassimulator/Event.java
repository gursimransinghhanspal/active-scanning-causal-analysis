package com.gursimransinghhanspal.powerstateassimulator;

import java.util.Calendar;

public class Event {

	private long epoch_ts;
	private EventType type;

	public enum EventType {
		WAKELOCK_ACQUIRED,
		WAKELOCK_RELEASED,
		SIMULATION_STARTED,
		SIMULATION_ENDED
	}

	public Event() {
		Calendar calendar = Calendar.getInstance();
		this.epoch_ts = calendar.getTimeInMillis();
	}

	public Event(long epoch_ts, EventType type) {
		this.epoch_ts = epoch_ts;
		this.type = type;
	}

	public long getEpoch_ts() {
		return epoch_ts;
	}

	public EventType getType() {
		return type;
	}

	public void setType(EventType type) {
		this.type = type;
	}
}
