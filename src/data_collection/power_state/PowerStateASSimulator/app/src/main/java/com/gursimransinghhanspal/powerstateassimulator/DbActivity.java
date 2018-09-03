package com.gursimransinghhanspal.powerstateassimulator;

import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.os.Bundle;
import android.os.Environment;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.widget.Button;
import android.widget.TextView;

import com.opencsv.CSVWriter;

import java.io.File;
import java.io.FileWriter;
import java.util.Locale;

public class DbActivity extends AppCompatActivity {

	private static final String TAG = DbActivity.class.getSimpleName();

	TextView recentEventEpochTV, recentEventTypeTV, recordCountTV;
	Button refreshBtn, clearBtn, exportBtn;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_db);

		recentEventEpochTV = findViewById(R.id.activityLayout_db_eventEpochTV);
		recentEventTypeTV = findViewById(R.id.activityLayout_db_eventTypeTV);
		recordCountTV = findViewById(R.id.activityLayout_db_recordCountTV);
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
	}

	private void export() {

		File exportDir = new File(Environment.getExternalStorageDirectory(), Environment.DIRECTORY_DOWNLOADS);
		DBHelper dbHelper = new DBHelper(this);

		File file = new File(exportDir, "power_state_db.csv");
		try {
			file.createNewFile();
			CSVWriter csvWrite = new CSVWriter(new FileWriter(file));
			SQLiteDatabase db = dbHelper.getReadableDatabase();
			Cursor curCSV = dbHelper.getAllRecords();
			csvWrite.writeNext(curCSV.getColumnNames());
			while (curCSV.moveToNext()) {
				String arrStr[] = {curCSV.getString(0), curCSV.getString(1), curCSV.getString(2)};
				csvWrite.writeNext(arrStr);
			}
			csvWrite.close();
			curCSV.close();
		} catch (Exception sqlEx) {
			Log.e(TAG, sqlEx.getMessage(), sqlEx);
		}
	}
}
