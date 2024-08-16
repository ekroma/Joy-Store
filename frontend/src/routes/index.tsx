import { Route, Routes } from 'react-router-dom'
import AboutPage from '../components/about/AboutPage'
import AuthPage from '../components/auth/AuthPage'
import HomePage from '../components/home/HomePage'
import { LayoutWithSidebar } from '../layout/LayoutWithSidebar'

const AppRoutes = () => {
	return (
		<Routes>
			<Route element={<LayoutWithSidebar />}>
				<Route path='/' element={<HomePage />} />
				<Route path='/about' element={<AboutPage />} />
			</Route>
			<Route path='/login' element={<AuthPage />} />
		</Routes>
	)
}

export default AppRoutes
