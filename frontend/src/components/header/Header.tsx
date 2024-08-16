import React, { useEffect, useState } from "react";
import { useNavigate } from 'react-router-dom'
import './Header.scss'
import axios from "axios";
import { getUserProfile } from "../auth/AuthService";


export default function Header() {
    const [userName, setUserName] = useState(""); // Состояние для хранения имени пользователя
    const navigate = useNavigate()

    useEffect(() => {
        const fetchData = async () => {
          const userProfile = await getUserProfile();
          if (userProfile) {
            // Предположим, что имя пользователя доступно как userProfile.name
            setUserName(userProfile.first_name);
            };
        }
        fetchData();
        }
    , []);

    function deleteCookie(name) {
    document.cookie = name + '=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    }

    const logoutRequest = async () => {
		try {
			const res = await axios.post(
				'http://localhost:8000/online_store/v1/auth/logout',
                {},
                {
                    withCredentials: true,
                },
				deleteCookie('access_token'),
			)


			navigate('/login')
		} catch (e) {
			console.error(e)
		}
	}

    return (
        <header className="header">
        <ul className="header_profile">
             <input className="header_search"></input>
            <li>
                <svg className="header_svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"
                     xmlns="http://www.w3.org/2000/svg">
                    <path fillRule="evenodd" clipRule="evenodd"
                          d="M7.75 7.5C7.75 5.15279 9.65279 3.25 12 3.25C14.3472 3.25 16.25 5.15279 16.25 7.5C16.25 9.84721 14.3472 11.75 12 11.75C9.65279 11.75 7.75 9.84721 7.75 7.5ZM12 4.75C10.4812 4.75 9.25 5.98122 9.25 7.5C9.25 9.01878 10.4812 10.25 12 10.25C13.5188 10.25 14.75 9.01878 14.75 7.5C14.75 5.98122 13.5188 4.75 12 4.75Z"></path>
                    <path fillRule="evenodd" clipRule="evenodd"
                          d="M8 14.75C6.75736 14.75 5.75 15.7574 5.75 17V18.1883C5.75 18.2064 5.76311 18.2218 5.78097 18.2247C9.89972 18.8972 14.1003 18.8972 18.219 18.2247C18.2369 18.2218 18.25 18.2064 18.25 18.1883V17C18.25 15.7574 17.2426 14.75 16 14.75H15.6591C15.6328 14.75 15.6066 14.7542 15.5815 14.7623L14.716 15.045C12.9512 15.6212 11.0488 15.6212 9.28398 15.045L8.41847 14.7623C8.39342 14.7542 8.36722 14.75 8.34087 14.75H8ZM4.25 17C4.25 14.9289 5.92893 13.25 8 13.25H8.34087C8.52536 13.25 8.70869 13.2792 8.88407 13.3364L9.74959 13.6191C11.2119 14.0965 12.7881 14.0965 14.2504 13.6191L15.1159 13.3364C15.2913 13.2792 15.4746 13.25 15.6591 13.25H16C18.0711 13.25 19.75 14.9289 19.75 17V18.1883C19.75 18.9415 19.2041 19.5837 18.4607 19.7051C14.1819 20.4037 9.8181 20.4037 5.53927 19.7051C4.79588 19.5837 4.25 18.9415 4.25 18.1883V17Z"></path>
                </svg>
                <span className="header_nickname">{userName || "email"}</span>
                <span className="header_message">9</span>
            </li>
            <li>
                <a onClick={logoutRequest}>
                <svg className="header_svg_lougout" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"
                     xmlns="http://www.w3.org/2000/svg">
                    <path fillRule="evenodd" clipRule="evenodd"
                          d="M7.75 7.5C7.75 5.15279 9.65279 3.25 12 3.25C14.3472 3.25 16.25 5.15279 16.25 7.5C16.25 9.84721 14.3472 11.75 12 11.75C9.65279 11.75 7.75 9.84721 7.75 7.5ZM12 4.75C10.4812 4.75 9.25 5.98122 9.25 7.5C9.25 9.01878 10.4812 10.25 12 10.25C13.5188 10.25 14.75 9.01878 14.75 7.5C14.75 5.98122 13.5188 4.75 12 4.75Z"></path>
                    <path fillRule="evenodd" clipRule="evenodd"
                          d="M8 14.75C6.75736 14.75 5.75 15.7574 5.75 17V18.1883C5.75 18.2064 5.76311 18.2218 5.78097 18.2247C9.89972 18.8972 14.1003 18.8972 18.219 18.2247C18.2369 18.2218 18.25 18.2064 18.25 18.1883V17C18.25 15.7574 17.2426 14.75 16 14.75H15.6591C15.6328 14.75 15.6066 14.7542 15.5815 14.7623L14.716 15.045C12.9512 15.6212 11.0488 15.6212 9.28398 15.045L8.41847 14.7623C8.39342 14.7542 8.36722 14.75 8.34087 14.75H8ZM4.25 17C4.25 14.9289 5.92893 13.25 8 13.25H8.34087C8.52536 13.25 8.70869 13.2792 8.88407 13.3364L9.74959 13.6191C11.2119 14.0965 12.7881 14.0965 14.2504 13.6191L15.1159 13.3364C15.2913 13.2792 15.4746 13.25 15.6591 13.25H16C18.0711 13.25 19.75 14.9289 19.75 17V18.1883C19.75 18.9415 19.2041 19.5837 18.4607 19.7051C14.1819 20.4037 9.8181 20.4037 5.53927 19.7051C4.79588 19.5837 4.25 18.9415 4.25 18.1883V17Z"></path>
                </svg>
                </a>
            </li>
        </ul>
        </header>
    )
}