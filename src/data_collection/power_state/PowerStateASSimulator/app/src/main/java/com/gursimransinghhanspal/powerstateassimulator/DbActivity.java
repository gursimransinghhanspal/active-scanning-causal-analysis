package com.gursimransinghhanspal.powerstateassimulator;

import android.app.ProgressDialog;
import android.content.Context;
import android.database.Cursor;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.ref.WeakReference;
import java.util.Locale;

public class DbActivity extends AppCompatActivity implements View.OnClickListener {

	private static final String TAG = DbActivity.class.getSimpleName();

	TextView recentEventEpochTV, recentEventTypeTV, recordCountTV;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_db);

		recentEventEpochTV = findViewById(R.id.activityLayout_db_eventEpochTV);
		recentEventTypeTV = findViewById(R.id.activityLayout_db_eventTypeTV);
		recordCountTV = findViewById(R.id.activityLayout_db_recordCountTV);

		findViewById(R.id.activityLayout_db_refreshBtn).setOnClickListener(this);
		findViewById(R.id.activityLayout_db_clearBtn).setOnClickListener(this);
		findViewById(R.id.activityLayout_db_exportBtn).setOnClickListener(this);
	}

	@Override
	public void onClick(View view) {
		switch (view.getId()) {
			case R.id.activityLayout_db_refreshBtn:
				refresh();
				break;
			case R.id.activityLayout_db_clearBtn:
				clear();
				break;
			case R.id.activityLayout_db_exportBtn:
				export();
				break;
		}
	}

	private void refresh() {
		DBHelper dbHelper = new DBHelper(this);
		Event event = dbHelper.getMostRecentEvent();

		if (event != null) {
			recentEventEpochTV.setText(String.format(Locale.US, "%d", event.getEpoch_ts()));
			recentEventTypeTV.setText(String.format(Locale.US, "%s", event.getType().toString()));
			recordCountTV.setText(String.format(Locale.US, "%d", dbHelper.getRecordCount()));
		} else {
			recentEventEpochTV.setText("NA");
			recentEventTypeTV.setText("NA");
			recordCountTV.setText("NA");
		}
	}

	private void clear() {
		DBHelper dbHelper = new DBHelper(this);
		dbHelper.clearEvents();

		Toast.makeText(this, "Cleared!", Toast.LENGTH_LONG).show();
	}

	private void export() {
		new ExportDatabaseCSVTask(this).executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
	}

	public static class ExportDatabaseCSVTask extends AsyncTask<String, Void, Boolean> {

		private WeakReference<Context> activityReference;
		private final ProgressDialog dialog;
		DBHelper dbhelper;

		public ExportDatabaseCSVTask(Context context) {
			activityReference = new WeakReference<>(context);
			dialog = new ProgressDialog(context);
			dbhelper = new DBHelper(context);
		}

		@Override
		protected void onPreExecute() {
			this.dialog.setMessage("Exporting database...");
			this.dialog.show();
		}

		protected Boolean doInBackground(final String... args) {

			File exportDir = new File(Environment.getExternalStorageDirectory(), "/power_state_output/");
			if (!exportDir.exists()) {
				Boolean res = exportDir.mkdirs();
			}

			File file = new File(exportDir, "person.csv");
			try {
				Boolean res = file.createNewFile();
				CSVWriter csvWrite = new CSVWriter(new FileWriter(file));

				Cursor curCSV = dbhelper.getAllRecords();
				csvWrite.writeNext(curCSV.getColumnNames());

				while (curCSV.moveToNext()) {
					String[] mySecondStringArray = new String[curCSV.getColumnNames().length];
					mySecondStringArray[0] = Integer.toString(curCSV.getInt(0));
					mySecondStringArray[1] = Long.toString(curCSV.getLong(1));
					mySecondStringArray[2] = curCSV.getString(2);
					csvWrite.writeNext(mySecondStringArray);
				}

				csvWrite.close();
				curCSV.close();
				return true;

			} catch (IOException e) {
				return false;
			}
		}

		protected void onPostExecute(final Boolean success) {
			if (this.dialog.isShowing()) {
				this.dialog.dismiss();
			}

			Context context = activityReference.get();
			if (context != null) {
				if (success) {
					Toast.makeText(context, "Export successful!", Toast.LENGTH_SHORT).show();
				} else {
					Toast.makeText(context, "Export failed", Toast.LENGTH_SHORT).show();
				}
			}
		}
	}
}
