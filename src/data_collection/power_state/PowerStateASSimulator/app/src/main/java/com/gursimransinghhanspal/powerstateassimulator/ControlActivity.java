package com.gursimransinghhanspal.powerstateassimulator;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.PowerManager;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

import java.util.Locale;

public class ControlActivity extends AppCompatActivity implements View.OnClickListener {

	private static final String TAG = ControlActivity.class.getSimpleName();

	private static Long wakeLockCount = 0L;
	private static Boolean keepThreadRunning = null;
	private Thread controlThread;
	private DbHelper dbHelper;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_control);

		findViewById(R.id.activityLayout_control_startBtn).setOnClickListener(this);
		findViewById(R.id.activityLayout_control_stopBtn).setOnClickListener(this);
		findViewById(R.id.activityLayout_control_dbBtn).setOnClickListener(this);

		dbHelper = new DbHelper(this);

		// Enable Views
		findViewById(R.id.activityLayout_control_screenTimeoutInput).setEnabled(true);
		findViewById(R.id.activityLayout_control_intervalInput).setEnabled(true);
		findViewById(R.id.activityLayout_control_startBtn).setEnabled(true);
		findViewById(R.id.activityLayout_control_dbBtn).setEnabled(true);
		// Disable stop button
		findViewById(R.id.activityLayout_control_stopBtn).setEnabled(false);
	}

	@Override
	public void onClick(View view) {
		switch (view.getId()) {
			case R.id.activityLayout_control_startBtn:
				startSimulation();
				break;
			case R.id.activityLayout_control_stopBtn:
				stopSimulation();
				break;
			case R.id.activityLayout_control_dbBtn:
				Intent startDbActivityIntent = new Intent(this, DbActivity.class);
				startActivity(startDbActivityIntent);
				break;
		}
	}

	private void startSimulation() {

		EditText screenTimeoutInput = findViewById(R.id.activityLayout_control_screenTimeoutInput);
		String screenTimeout_asString = screenTimeoutInput.getText().toString();
		Integer screenTimeout_inMsec = null;
		try {
			Integer screenTimeout_inSec = Integer.valueOf(screenTimeout_asString);
			screenTimeout_inMsec = screenTimeout_inSec * 1000;
		} catch (NumberFormatException nfe) {
			Toast.makeText(
					this,
					"Error converting Screen Timeout to Integer!",
					Toast.LENGTH_LONG
			).show();
			return;
		}

		EditText intervalInput = findViewById(R.id.activityLayout_control_intervalInput);
		String interval_asString = intervalInput.getText().toString();
		Integer interval_inMsec = null;
		try {
			Integer interval_inSec = Integer.valueOf(interval_asString);
			interval_inMsec = interval_inSec * 1000;
		} catch (NumberFormatException nfe) {
			Toast.makeText(
					this,
					"Error converting Interval to Integer!",
					Toast.LENGTH_LONG
			).show();
			return;
		}

		final Integer ScreenTimeout_inMsec = screenTimeout_inMsec;
		final Integer HalfCycleInterval_inMsec = interval_inMsec;

		keepThreadRunning = true;
		controlThread = new Thread() {

			private final int HALF_CYCLE_INTERVAL_MSEC = HalfCycleInterval_inMsec;
			private final int DEVICE_SCREEN_TIMEOUT_MSEC = ScreenTimeout_inMsec;

			/* **
			 * Cycle length = Screen On Time + Screen Timeout + Screen Off Time
			 */

			@Override
			public void run() {
				while (keepThreadRunning) {
					PowerManager.WakeLock wakeLock = acquireWakeLock(HALF_CYCLE_INTERVAL_MSEC, DEVICE_SCREEN_TIMEOUT_MSEC);

					// Time that screen stays on = HALF_CYCLE_INTERVAL_MSEC
					try {
						Thread.sleep(HALF_CYCLE_INTERVAL_MSEC);
					} catch (InterruptedException ignored) {
					}

					releaseWakeLock(wakeLock);

					// Time it takes for the screen to turn off automatically = DEVICE_SCREEN_TIMEOUT_MSEC
					// Time the screen stays off = HALF_CYCLE_INTERVAL_MSEC
					try {
						Thread.sleep(DEVICE_SCREEN_TIMEOUT_MSEC + HALF_CYCLE_INTERVAL_MSEC);
					} catch (InterruptedException ignored) {
					}
				}
			}
		};

		// Disable views
		findViewById(R.id.activityLayout_control_screenTimeoutInput).setEnabled(false);
		findViewById(R.id.activityLayout_control_intervalInput).setEnabled(false);
		findViewById(R.id.activityLayout_control_startBtn).setEnabled(false);
		findViewById(R.id.activityLayout_control_dbBtn).setEnabled(false);
		// Enable stop button
		findViewById(R.id.activityLayout_control_stopBtn).setEnabled(true);

		// start cycle
		controlThread.start();

		Event simulationStarted = new Event();
		simulationStarted.setType(Event.EventType.SIMULATION_STARTED);
		dbHelper.insertEvent(simulationStarted);
	}

	private void stopSimulation() {
		if (controlThread != null && controlThread.isAlive()) {
			keepThreadRunning = false;
			try {
				controlThread.join(1000L);
				controlThread = null;

				// Enable Views
				findViewById(R.id.activityLayout_control_screenTimeoutInput).setEnabled(true);
				findViewById(R.id.activityLayout_control_intervalInput).setEnabled(true);
				findViewById(R.id.activityLayout_control_startBtn).setEnabled(true);
				findViewById(R.id.activityLayout_control_dbBtn).setEnabled(true);
				// Disable stop button
				findViewById(R.id.activityLayout_control_stopBtn).setEnabled(false);

				Event simulationEnded = new Event();
				simulationEnded.setType(Event.EventType.SIMULATION_ENDED);
				dbHelper.insertEvent(simulationEnded);

			} catch (InterruptedException ignore) {

			}
		} else {
			// Enable Views
			findViewById(R.id.activityLayout_control_screenTimeoutInput).setEnabled(true);
			findViewById(R.id.activityLayout_control_intervalInput).setEnabled(true);
			findViewById(R.id.activityLayout_control_startBtn).setEnabled(true);
			findViewById(R.id.activityLayout_control_dbBtn).setEnabled(true);
			// Disable stop button
			findViewById(R.id.activityLayout_control_stopBtn).setEnabled(false);
		}
	}

	private PowerManager.WakeLock acquireWakeLock(int halfCycleInterval, int screenTimeout) {

		Log.i(TAG, "acquireWakeLock(): begin");

		PowerManager powerManager = (PowerManager) getSystemService(Context.POWER_SERVICE);
		if (powerManager != null) {

			Log.i(TAG, "acquireWakeLock(): Power Service fetched!");

			wakeLockCount++;
			PowerManager.WakeLock wakeLock = powerManager.newWakeLock(
					PowerManager.FULL_WAKE_LOCK | PowerManager.ACQUIRE_CAUSES_WAKEUP,
					String.format(Locale.US, "%d", wakeLockCount)
			);

			if (wakeLock != null) {
				Log.i(TAG, "acquireWakeLock(): WakeLock created!");

				// any wakelock can't be required for more than this
				int maxTimeout = (halfCycleInterval * 3) + screenTimeout;
				wakeLock.acquire(maxTimeout);
				Log.i(TAG, "acquireWakeLock(): WakeLock acquired!");
				ControlActivity.this.runOnUiThread(
						new Runnable() {
							@Override
							public void run() {
								Toast.makeText(ControlActivity.this, "WakeLock Acquired!", Toast.LENGTH_LONG).show();
							}
						}
				);

				Event wakelockAcquired = new Event();
				wakelockAcquired.setType(Event.EventType.WAKELOCK_ACQUIRED);
				dbHelper.insertEvent(wakelockAcquired);
				return wakeLock;

			} else {
				Log.e(TAG, "acquireWakeLock(): WakeLock couldn't be created!");
				ControlActivity.this.runOnUiThread(
						new Runnable() {
							@Override
							public void run() {
								Toast.makeText(ControlActivity.this, "WakeLock Acquiring Failed!", Toast.LENGTH_LONG).show();
							}
						}
				);
			}

		} else {
			Log.e(TAG, "acquireWakeLock(): Power Service couldn't be fetched!");
			ControlActivity.this.runOnUiThread(
					new Runnable() {
						@Override
						public void run() {
							Toast.makeText(ControlActivity.this, "WakeLock Acquiring Failed 2!", Toast.LENGTH_LONG).show();
						}
					}
			);
		}

		return null;
	}

	private void releaseWakeLock(PowerManager.WakeLock wakeLock) {
		Log.i(TAG, "releaseWakeLock(): begin");

		if (wakeLock != null) {
			wakeLock.release();
			Log.i(TAG, "releaseWakeLock(): WakeLock released!");
			ControlActivity.this.runOnUiThread(
					new Runnable() {
						@Override
						public void run() {
							Toast.makeText(ControlActivity.this, "WakeLock Released!", Toast.LENGTH_LONG).show();
						}
					}
			);

			Event wakelockReleased = new Event();
			wakelockReleased.setType(Event.EventType.WAKELOCK_RELEASED);
			dbHelper.insertEvent(wakelockReleased);

		} else {
			Log.e(TAG, "releaseWakeLock(): WakeLock was null!");
			ControlActivity.this.runOnUiThread(
					new Runnable() {
						@Override
						public void run() {
							Toast.makeText(ControlActivity.this, "WakeLock Releasing Failed!", Toast.LENGTH_LONG).show();
						}
					}
			);
		}
	}
}
