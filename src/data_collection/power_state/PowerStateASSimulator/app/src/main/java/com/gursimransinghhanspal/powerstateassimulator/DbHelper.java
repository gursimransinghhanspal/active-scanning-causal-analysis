package com.gursimransinghhanspal.powerstateassimulator;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class DbHelper extends SQLiteOpenHelper {

	private static final int DB_VER = 1;
	private static final String DB_NAME = "com_gursimransinghhanspal_powerstateassimulator.db";
	private static final String TBL_NAME = "events";
	private static final String COL_1 = "id";
	private static final String COL_2 = "timestamp";
	private static final String COL_3 = "type";


	public DbHelper(Context context) {
		super(context, DB_NAME, null, DB_VER);
	}

	@Override
	public void onCreate(SQLiteDatabase sqLiteDatabase) {
		sqLiteDatabase.execSQL(
				"CREATE TABLE IF NOT EXISTS " + TBL_NAME + " (" +
						COL_1 + " INTEGER PRIMARY KEY AUTOINCREMENT," +
						COL_2 + " INTEGER," +
						COL_3 + " TEXT" +
						")"
		);
	}

	@Override
	public void onUpgrade(SQLiteDatabase sqLiteDatabase, int i, int i1) {
		sqLiteDatabase.execSQL(
				"DROP TABLE IF EXISTS " + TBL_NAME
		);
		onCreate(sqLiteDatabase);
	}

	public long insertEvent(Event event) {
		SQLiteDatabase sqLiteDatabase = getWritableDatabase();

		//
		ContentValues contentValues = new ContentValues();
		contentValues.put(COL_2, event.getEpoch_ts());
		contentValues.put(COL_3, event.getType().toString());

		//
		return sqLiteDatabase.insert(TBL_NAME, null, contentValues);
	}

	public void clearEvents() {
		SQLiteDatabase sqLiteDatabase = getWritableDatabase();
		sqLiteDatabase.execSQL(
				"DROP TABLE IF EXISTS " + TBL_NAME
		);
		onCreate(sqLiteDatabase);
	}

	public Event getMostRecentEvent() {
		SQLiteDatabase sqLiteDatabase = getReadableDatabase();
		Cursor cursor = sqLiteDatabase.rawQuery(
				"SELECT * FROM " + TBL_NAME + " ORDER BY " + COL_2 + " DESC",
				null
		);
		if (cursor.getCount() == 0) {
			cursor.close();
			return null;
		}

		cursor.moveToFirst();
		Event event = new Event(cursor.getLong(1), Event.EventType.valueOf(cursor.getString(2)));
		cursor.close();
		return event;
	}

	public int getRecordCount() {
		SQLiteDatabase sqLiteDatabase = getReadableDatabase();
		Cursor cursor = sqLiteDatabase.rawQuery(
				"SELECT * FROM " + TBL_NAME,
				null
		);
		int count = cursor.getCount();
		cursor.close();
		return count;
	}

	public Cursor getAllRecords() {
		SQLiteDatabase sqLiteDatabase = getReadableDatabase();
		Cursor cursor = sqLiteDatabase.rawQuery(
				"SELECT * FROM " + TBL_NAME,
				null
		);
		return cursor;
	}
}
