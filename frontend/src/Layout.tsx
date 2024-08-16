import Sidebar from "./components/sidebar/Sidebar";
import { Outlet } from 'react-router-dom';

const LayoutWithSidebar = () => {
  return (
    <div>
      <Sidebar />
      <Outlet />
    </div>
  );
}

export default LayoutWithSidebar;