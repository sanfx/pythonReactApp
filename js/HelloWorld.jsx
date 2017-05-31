export class HelloWorld extends React.Component {
  render() {
    return (
      <div className="helloworld">
        Isomorphic Hello {this.props.name}
      </div>
    );
  }
}
