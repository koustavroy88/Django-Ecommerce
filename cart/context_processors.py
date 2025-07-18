from .cart import Cart

# create context processor so that the cart can work in all pages of the site
def cart(request):
    # return the default data from our cart
    return {'cart':Cart(request)}