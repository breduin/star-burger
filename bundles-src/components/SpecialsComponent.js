import React, {Component} from 'react';
import Product from './Product';
import LoadingProducts from './loaders/LoadingProducts';
import NoResults from "./NoResults";
import CSSTransitionGroup from 'react-transition-group/CSSTransitionGroup';

class SpecialsComponent extends Component{
  render(){
    let productsData;
    let term = this.props.term.toLowerCase();

    productsData = this.props.productsList.filter(x => {
      return x.name.toLowerCase().includes(term) || !term;
    }).filter(x => {
      return x.special_status == true;
    }).map(product =>{
      return (
        <Product
          key={product.id}
          product={product}
          addToCart={this.props.addToCart}
          productQuantity={this.props.productQuantity}
          updateQuantity={this.props.updateQuantity}
          openModal={this.props.openModal}
        />
      )
    });

    // Empty and Loading States
    let view;
    if(productsData.length <= 0 && !term){
      view = <LoadingProducts />
    } else if(productsData.length <= 0 && term){
      view = '';
    } else{
      view = (
        <CSSTransitionGroup
          transitionName="fadeIn"
          transitionEnterTimeout={500}
          transitionLeaveTimeout={300}
          component="div"
          className="products">
          {productsData}
        </CSSTransitionGroup>
      )
    }
    return (
      <div className="products-wrapper">
        {view}
      </div>
    )
  }
}

export default SpecialsComponent;