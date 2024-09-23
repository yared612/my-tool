import React from "react";
import Calendar from "../../components/calendar/Calendar";

const CalendarPage: React.FC = () => {
  return (
    <div>
      <h1 style={{justifyContent: "center", display: "flex"}}>shift schedule</h1>
      <Calendar />
    </div>
  );
};

export default CalendarPage;
