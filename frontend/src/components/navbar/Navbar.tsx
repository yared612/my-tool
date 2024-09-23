import { PageUser } from "../../App";
import './Navbar.css';

interface NavbarProps {
  user: PageUser | null;
  toggleSidebar: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ user, toggleSidebar }) => {
  return (
    <div className="navbar">
      <button className="menu-button" onClick={toggleSidebar}>
        ☰
      </button>
      {user ? (
        <div className="user-info">
          <p>{user.name}</p>
        </div>
      ) : (
        <p style={{marginRight: "32px"}}>Loading user info...</p>
      )}
    </div>
  );
};

export default Navbar;
