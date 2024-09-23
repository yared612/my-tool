import { Box, Button, Tab, Tabs } from '@mui/material';
import { format, getDay, parse, startOfWeek } from 'date-fns';
import zhTW from 'date-fns/locale/zh-TW';
import React, { useContext, useEffect, useState } from 'react';
import {
    Calendar as BigCalendar,
    dateFnsLocalizer,
} from 'react-big-calendar';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { AuthContext } from '../../utils/AuthContext';
import axios from '../../utils/axiosConfig';
import './Calendar.css';

const locales = {
  'zh-TW': zhTW,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek: () => startOfWeek(new Date(), { weekStartsOn: 1 }),
  getDay,
  locales,
});

interface MyEvent {
  title: string;
  start: Date;
  end: Date;
  allDay?: boolean;
  shift: string;
  employees: string[];
}

const Calendar: React.FC = () => {
  const { user, logout } = useContext(AuthContext);
  const [tabValue, setTabValue] = useState(0);
  const [dayEvents, setDayEvents] = useState<MyEvent[]>([]);
  const [swingEvents, setSwingEvents] = useState<MyEvent[]>([]);
  const [nightEvents, setNightEvents] = useState<MyEvent[]>([]);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedEmployees, setSelectedEmployees] = useState<string[]>([]);
  const [currentMonth, setCurrentMonth] = useState<number>(new Date().getMonth());

  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        console.log('Fetching schedule...');
        const response = await axios.get('/api/schedule'); 
        const data = response.data;
        console.log('Schedule data:', data);
        const events: MyEvent[] = [];

        const currentYear = new Date().getFullYear();
        const currentMonth = new Date().getMonth();

        Object.keys(data).forEach((dayKey) => {
          const day = parseInt(dayKey.replace('Day ', ''), 10);
          const date = new Date(currentYear, currentMonth, day);
          date.setHours(0, 0, 0, 0);

          const dayData = data[dayKey];

          Object.keys(dayData).forEach((shift) => {
            const employees = dayData[shift];
            const title = `${shift.toUpperCase()} Shift: ${employees.join(', ')}`;

            events.push({
              title,
              start: new Date(date),
              end: new Date(date),
              allDay: true,
              shift,
              employees,
            });
          });
        });

        // Distinguish day shift, swing shift and night shift
        setDayEvents(events.filter((event) => event.shift === 'day'));
        setSwingEvents(events.filter((event) => event.shift === 'swing'));
        setNightEvents(events.filter((event) => event.shift === 'night'));
      } catch (error) {
        console.error('Failed to fetch schedule:', error);
      }
    };

    fetchSchedule();
  }, []);

  // Auto-select today when events are loaded.
  useEffect(() => {
    if (selectedDate === null && (dayEvents.length > 0 || swingEvents.length > 0 || nightEvents.length > 0)) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      console.log('Auto-selecting today:', today);
      processDateSelection(today);
    }
  }, [dayEvents, swingEvents, nightEvents]);

  const currentEvents =
    tabValue === 0 ? dayEvents : tabValue === 1 ? swingEvents : nightEvents;

  const eventStyleGetter = (
    event: MyEvent,
    start: Date,
    end: Date,
    isSelected: boolean
  ) => {
    let backgroundColor = '#3174ad';

    if (event.shift === 'day') {
      backgroundColor = '#1e90ff';
    } else if (event.shift === 'swing') {
      backgroundColor = '#ff8c00';
    } else if (event.shift === 'night') {
      backgroundColor = '#6a5acd';
    }

    const style = {
      backgroundColor,
      borderRadius: '0px',
      opacity: 0.8,
      color: 'white',
      border: isSelected ? '2px solid red' : '0px',
      display: 'block',
    };

    return {
      style,
    };
  };

  const handleTabChange = (event: React.ChangeEvent<{}>, newValue: number) => {
    setTabValue(newValue);
    // Update employees when switching tabs.
    if (selectedDate) {
      processDateSelection(selectedDate, newValue);
    }
  };

  const processDateSelection = (date: Date, tabIndex: number = tabValue) => {
    const selectedDate = new Date(date);
    selectedDate.setHours(0, 0, 0, 0);

    const eventsOnDate =
      (tabIndex === 0 ? dayEvents : tabIndex === 1 ? swingEvents : nightEvents).filter((event) => {
        const eventDate = new Date(event.start);
        eventDate.setHours(0, 0, 0, 0);
        return eventDate.getTime() === selectedDate.getTime();
      });

    const employees = eventsOnDate.flatMap((event) => event.employees);

    setSelectedDate(selectedDate);
    setSelectedEmployees(employees);
    console.log('Selected date:', selectedDate);
    console.log('Employees:', employees);
  };

  const handleDateSelect = (slotInfo: {
    start: Date;
    end: Date;
    action: 'select' | 'click' | 'doubleClick';
  }) => {
    const date = slotInfo.start;
    console.log('Date selected:', date);

    if (date.getMonth() !== currentMonth) {
      console.log('Selected date is not in current month. Ignoring.');
      return;
    }

    processDateSelection(date);
  };

  const handleEventSelect = (event: MyEvent) => {
    const date = event.start;
    console.log('Event selected:', event);

    if (date.getMonth() !== currentMonth) {
      console.log('Event date is not in current month. Ignoring.');
      return;
    }

    processDateSelection(date);
  };

  const dayPropGetter = (date: Date) => {
    const isCurrentMonth = date.getMonth() === currentMonth;
    const selected =
      selectedDate &&
      date.getFullYear() === selectedDate.getFullYear() &&
      date.getMonth() === selectedDate.getMonth() &&
      date.getDate() === selectedDate.getDate();

    let className = 'custom-date-cell';

    if (selected) {
      className += ' selected-date-cell';
    }

    if (!isCurrentMonth) {
      className += ' disabled-date-cell';
    }

    return {
      className,
    };
  };

  const handleNavigate = (date: Date) => {
    setCurrentMonth(date.getMonth());
    console.log('Navigated to month:', date.getMonth());
  };

  const renderCalendar = (eventsToShow: MyEvent[]) => (
    <BigCalendar
      localizer={localizer}
      events={eventsToShow}
      startAccessor="start"
      endAccessor="end"
      views={['month']}
      style={{ height: 600 }}
      culture="zh-TW"
      eventPropGetter={eventStyleGetter}
      dayPropGetter={dayPropGetter}
      selectable
      onSelectSlot={handleDateSelect}
      onSelectEvent={handleEventSelect}
      onNavigate={handleNavigate}
      messages={{
        next: '下個月',
        previous: '上個月',
        today: '今天',
        month: '月',
        week: '週',
        day: '日',
        agenda: '班程',
        date: '日期',
        time: '時間',
        event: '事件',
        allDay: '全天',
        noEventsInRange: '這個範圍内沒有事件',
      }}
      drilldownView={null}
    />
  );

  return (
    <div>
      <Box sx={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px' }}>
        <Tabs value={tabValue} onChange={handleTabChange} centered>
          <Tab label="Day Shift" />
          <Tab label="Swing Shift" />
          <Tab label="Night Shift" />
        </Tabs>
        <Button variant="contained" color="secondary" onClick={logout}>
          Logout
        </Button>
      </Box>
      {tabValue === 0 && renderCalendar(dayEvents)}
      {tabValue === 1 && renderCalendar(swingEvents)}
      {tabValue === 2 && renderCalendar(nightEvents)}

      {selectedDate && (
        <div>
          <h3>
            {selectedDate.toLocaleDateString('zh-TW', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}{' '}
            的上班人員：
          </h3>
          {selectedEmployees.length > 0 ? (
            <ul>
              {selectedEmployees.map((employee, index) => (
                <li key={index}>{employee}</li>
              ))}
            </ul>
          ) : (
            <p>無上班人員。</p>
          )}
        </div>
      )}
    </div>
  );
};

export default Calendar;
