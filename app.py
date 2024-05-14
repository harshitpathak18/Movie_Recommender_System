# from streamlit_player import st_player
import streamlit as st
import pickle
import pandas as pd
import requests
import gzip

st.set_page_config(layout="wide")

movies_dict=pickle.load(open('movies_dict.pkl','rb'))
similarity=pickle.load(open('similarity.pkl','rb'))
movies = pd.DataFrame(movies_dict)

# with gzip.open('similarity1.pkl.gz', 'rb') as f:
#     similarity = pickle.load(f)


def fetch_poster(movie_id):
    response=requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=96aef6c0d373ea579771046d96e72e06")
    data=response.json()
    return "https://image.tmdb.org/t/p/w500/"+data['poster_path']

def fetch_youtube(movie_id):
    response=requests.get(f"http://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=96aef6c0d373ea579771046d96e72e06")
    data=response.json()

    return "https://www.youtube.com/watch?v="+data["results"][0]["key"]

def fetch_detail(movie_id):
    response=requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=96aef6c0d373ea579771046d96e72e06")
    data=response.json()
    
    detail={"Description":data['overview'],
            "Genres":[i['name'] for i in data['genres']],
            "Rating":data['vote_average']
           }
    return detail

def fetch_cast(movie_id):
    response=requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=96aef6c0d373ea579771046d96e72e06&append_to_response=credits")
    data=response.json()
    name=[]
    image=[]
    for i in data['credits']['cast'][0:5]:
        name.append(i['name'])
        image.append("https://image.tmdb.org/t/p/w600_and_h900_bestv2"+i['profile_path'])
        
    return dict({"Name":name,"Image":image})

def fetch_director(movie_id):
    response=requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=96aef6c0d373ea579771046d96e72e06&append_to_response=credits")
    data=response.json()
    director_name=[]
    director_image=[]
    for i in data['credits']['crew']:
        if i['job']=='Director':
            director_name.append(i['name'])
            director_image.append("https://image.tmdb.org/t/p/w600_and_h900_bestv2"+i['profile_path'])
            
            break
    return dict({"Name":director_name,"Image":director_image})

def recommend(movie):
    movie_index=movies[movies['title']==movie].index[0] 
    distances=similarity[movie_index]
    movies_list=sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:6]
    
    recommended_movies=[]
    recommended_movies_poster=[]
    recommended_movies_trailer=[]
    recommended_movies_details=[]
    casts=[]
    director=[]

    for i in movies_list:
        # fetch youtube video
        recommended_movies_trailer.append(fetch_youtube(movies.iloc[i[0]].id))
        
        # fetch poster using Api
        recommended_movies_poster.append(fetch_poster(movies.iloc[i[0]].id))
        
        # fetching moving title
        recommended_movies.append(movies.iloc[i[0]].title)

        # fetching other details
        recommended_movies_details.append(fetch_detail(movies.iloc[i[0]].id))

        # fetching cast
        casts.append(fetch_cast(movies.iloc[i[0]].id))

        # fetching director
        director.append(fetch_director(movies.iloc[i[0]].id))


    return recommended_movies,recommended_movies_poster,recommended_movies_trailer,recommended_movies_details,casts,director


st.title("Movie Recommender System")

movie=st.selectbox("Select a movie",movies['title'].values)


if st.button("Recommend"):
    st.subheader(f"Movies like {movie}")

    title,poster,trailer,detail,casts,directors=recommend(movie)

    for i in range(5):
        st.write("")
        tab1, tab2 = st.tabs(["Movie Datails","Trailer"])

        with tab1:
            col1,col2=st.columns(2)

            with col1:
                st.image(poster[i])
            with col2:
                st.subheader(title[i])            
                
                st.subheader(f"Summary-")
                st.write(detail[i]['Description'])

                st.markdown( f"Rating - :star2: {detail[i]['Rating']}")

                st.write(f"Genre - {', '.join(detail[i]['Genres'])}")

                st.subheader("Cast:")
                col1,col2,col3,col4,col5=st.columns(5)
                
                with col1:
                    st.image(casts[i]['Image'][0])
                    st.write(casts[i]['Name'][0])

                with col2:
                    st.image(casts[i]['Image'][1])
                    st.write(casts[i]['Name'][1])

                with col3:
                    st.image(casts[i]['Image'][2])
                    st.write(casts[i]['Name'][2])

                with col4:
                    st.image(casts[i]['Image'][3])
                    st.write(casts[i]['Name'][3])

                with col5:
                    st.image(casts[i]['Image'][4])
                    st.write(casts[i]['Name'][4])

                st.subheader("Director:")
                col1,col2,col3,col4,col5=st.columns(5)
                with col1:
                    st.image(directors[i]['Image'][0])
                    st.write(directors[i]['Name'][0])


        with tab2:
            st.subheader(f"Trailer - {title[i]}") 
            st_player(trailer[i])

        st.write("")
        st.write("")
