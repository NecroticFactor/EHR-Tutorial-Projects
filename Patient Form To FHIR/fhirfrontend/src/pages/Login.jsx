import Form from "../components/UserForm";

function Login() {
  return <Form route="api/token/" method="login" />;
}

export default Login;
