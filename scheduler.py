import requests
from datetime import datetime, timedelta

class Scheduler:
    def __init__(self, url: str):
        self.url = url
        self._load_data()

    def _load_data(self):
        r = requests.get(self.url)
        r.raise_for_status()
        data = r.json()
        self.days = {d['id']: d for d in data['days']}
        self.timeslots = data['timeslots']

    def _get_day(self, date_str):
        for d in self.days.values():
            if d['date'] == date_str:
                return d
        return None

    def get_busy_slots(self, date_str):
        day = self._get_day(date_str)
        if not day:
            return []
        busy = [
            (ts['start'], ts['end'])
            for ts in self.timeslots if ts['day_id'] == day['id']
        ]
        # сортировка по началу
        return sorted(busy, key=lambda x: x[0])

    def get_free_slots(self, date_str):
        day = self._get_day(date_str)
        if not day:
            return []
        start_work = day['start']
        end_work = day['end']
        busy = self.get_busy_slots(date_str)

        free = []
        cursor = datetime.strptime(start_work, '%H:%M')
        end_day = datetime.strptime(end_work, '%H:%M')

        for bstart, bend in busy:
            bs = datetime.strptime(bstart, '%H:%M')
            be = datetime.strptime(bend, '%H:%M')
            if cursor < bs:
                free.append((cursor.strftime('%H:%M'), bstart))
            cursor = max(cursor, be)
        if cursor < end_day:
            free.append((cursor.strftime('%H:%M'), end_work))
        return free

    def is_available(self, date_str, start, end):
        free = self.get_free_slots(date_str)
        return any(fs <= start and fe >= end for fs, fe in free)

    def find_slot_for_duration(self, duration_minutes):
        # ищем по всем дням в хронологическом порядке
        for day in sorted(self.days.values(), key=lambda d: d['date']):
            free = self.get_free_slots(day['date'])
            for fs, fe in free:
                tfs = datetime.strptime(fs, '%H:%M')
                tfe = datetime.strptime(fe, '%H:%M')
                if (tfe - tfs).seconds >= duration_minutes * 60:
                    end_slot = (tfs + timedelta(minutes=duration_minutes)).strftime('%H:%M')
                    return (day['date'], fs, end_slot)
        return None
