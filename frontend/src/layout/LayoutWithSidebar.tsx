import { Outlet } from 'react-router-dom'
import Sidebar from '../components/sidebar/Sidebar'

export const LayoutWithSidebar = () => {
	return (
		<div>
			<Sidebar />
			<Outlet />
		</div>
	)
}
