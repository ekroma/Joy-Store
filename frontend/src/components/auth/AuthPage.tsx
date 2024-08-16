import axios from 'axios'
import { ChangeEvent, FormEvent, useState } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import Button from '../button/Button'

import './AuthPage.scss'

const AuthPage: React.FC = () => {
	const navigate = useNavigate()
	const [loginForm, setLoginForm] = useState({
		email: '',
		password: '',
	})

	const handleLoginSubmit = (
		e: FormEvent<HTMLFormElement> | ChangeEvent<HTMLInputElement>
	) => {
		e.preventDefault()
		const { name, value } = e.target as HTMLInputElement
		setLoginForm(prevLoginForm => ({
			...prevLoginForm,
			[name]: value,
		}))
	}

	const loginRequest = async () => {
		try {
			const res = await axios.post(
				'http://localhost:8000/online_store/v1/auth/login-user',
				loginForm,
				{
					withCredentials: true,
				}
			)


			navigate('/')
		} catch (e) {
			console.error(e)
		}
	}

	return (
		<div className={'LoginFormContainer'}>
			<h1>Login</h1>
			<form onSubmit={handleLoginSubmit} className={'form'}>
				<label htmlFor='email'>Email:</label>
				<input
					type='email'
					name='email'
					placeholder='Введите почту'
					value={loginForm.email}
					onChange={e => handleLoginSubmit(e)}
				/>
				<label htmlFor='password'>Password:</label>
				<input
					type='password'
					name='password'
					placeholder='Введите пароль'
					value={loginForm.password}
					onChange={e => handleLoginSubmit(e)}
				/>
				<Button type='submit' buttonType='login' onClick={loginRequest}>
					Вход
				</Button>

			</form>
			<Outlet />
		</div>
	)
}

export default AuthPage
