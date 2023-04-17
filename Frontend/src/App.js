import React, { useState, useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./views/Home";
import Login from "./views/Login";
import Signup from "./views/Signup";
import AlertMessage from "./components/AlertMessage";
import Navbar from "./components/Navbar";
import Create from "./views/CreatePost";
import EditPost from "./views/EditPost";

export default function App() {
	// const now = new Date();

	const [loggedIn, setLoggedIn] = useState(
		localStorage.getItem("token") ? true : false
	);
	const [message, setMessage] = useState(null);
	const [category, setCategory] = useState(null);
	const [user, setUser] = useState({});

	useEffect(() => {
		if (loggedIn) {
			async function fetchLoggedInUser() {
				let myHeaders = new Headers();
				const token = localStorage.getItem("token");
				myHeaders.append("Authorization", `Bearer ${token}`);
				let response = await fetch(
					"https://api.spoonacular.com/recipes/random",
					{
						headers: myHeaders,
					}
				);
				let data = await response.json();
				if (data.error) {
					console.warn(data.error);
				} else {
					setUser(data);
				}
			}
			fetchLoggedInUser();
		}
	}, [loggedIn]);

	function flashMessage(message, category) {
		setMessage(message);
		setCategory(category);
	}

	function logUserIn() {
		setLoggedIn(true);
	}

	function logUserOut() {
		setLoggedIn(false);
		setUser({});
		localStorage.removeItem("token");
		// localStorage.removeItem('tokenExp');
		flashMessage("You have logged out", "success");
	}

	return (
		<>
			<Navbar loggedIn={loggedIn} logUserOut={logUserOut} />
			<div className="container">
				{message ? (
					<AlertMessage
						flashMessage={flashMessage}
						message={message}
						category={category}
					/>
				) : null}
				<Routes>
					<Route path="/" element={<Home user={user} loggedIn={loggedIn} />} />
					<Route
						path="/signup"
						element={<Signup flashMessage={flashMessage} />}
					/>
					<Route
						path="/login"
						element={
							<Login flashMessage={flashMessage} logUserIn={logUserIn} />
						}
					/>
					<Route
						path="/create"
						element={<Create flashMessage={flashMessage} loggedIn={loggedIn} />}
					/>
					<Route
						path="/edit/:postId"
						element={
							<EditPost flashMessage={flashMessage} loggedIn={loggedIn} />
						}
					/>
				</Routes>
			</div>
		</>
	);
}